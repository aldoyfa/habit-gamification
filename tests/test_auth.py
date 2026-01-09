"""
Unit tests for authentication module (JWT, token handling, user auth).
"""
import pytest
from datetime import timedelta
from uuid import uuid4
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.auth import (
    create_access_token,
    decode_access_token,
    get_current_user,
    authenticate_user,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.models import User
from app.repository import user_repository


class TestCreateAccessToken:
    """Tests for create_access_token function."""

    def test_create_token_basic(self):
        """Test creating a basic access token."""
        data = {"sub": str(uuid4())}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_token_with_custom_expiry(self):
        """Test creating token with custom expiration."""
        data = {"sub": str(uuid4())}
        expires_delta = timedelta(hours=2)
        
        token = create_access_token(data, expires_delta=expires_delta)
        
        assert token is not None
        decoded = decode_access_token(token)
        assert "exp" in decoded

    def test_create_token_preserves_data(self):
        """Test that token preserves original data."""
        user_id = str(uuid4())
        data = {"sub": user_id, "custom_claim": "test_value"}
        
        token = create_access_token(data)
        decoded = decode_access_token(token)
        
        assert decoded["sub"] == user_id
        assert decoded["custom_claim"] == "test_value"

    def test_create_token_adds_expiration(self):
        """Test that token includes expiration claim."""
        data = {"sub": str(uuid4())}
        
        token = create_access_token(data)
        decoded = decode_access_token(token)
        
        assert "exp" in decoded

    def test_create_token_different_for_same_data(self):
        """Test tokens can differ even with same data (due to exp time)."""
        data = {"sub": str(uuid4())}
        
        token1 = create_access_token(data)
        token2 = create_access_token(data)
        
        # Tokens might be same if created in same second, but should decode successfully
        decoded1 = decode_access_token(token1)
        decoded2 = decode_access_token(token2)
        assert decoded1["sub"] == decoded2["sub"]


class TestDecodeAccessToken:
    """Tests for decode_access_token function."""

    def test_decode_valid_token(self):
        """Test decoding a valid token."""
        user_id = str(uuid4())
        token = create_access_token({"sub": user_id})
        
        decoded = decode_access_token(token)
        
        assert decoded["sub"] == user_id

    def test_decode_invalid_token(self):
        """Test decoding an invalid token raises exception."""
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token("invalid.token.here")
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail

    def test_decode_tampered_token(self):
        """Test decoding a tampered token raises exception."""
        token = create_access_token({"sub": str(uuid4())})
        tampered_token = token[:-10] + "tamperedxx"
        
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(tampered_token)
        
        assert exc_info.value.status_code == 401

    def test_decode_empty_token(self):
        """Test decoding an empty token raises exception."""
        with pytest.raises(HTTPException):
            decode_access_token("")

    def test_decode_expired_token(self):
        """Test decoding an expired token raises exception."""
        token = create_access_token(
            {"sub": str(uuid4())},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)
        
        assert exc_info.value.status_code == 401


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""

    def test_get_current_user_valid(self, test_user):
        """Test getting current user with valid token."""
        token = create_access_token({"sub": str(test_user.user_id)})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        user = get_current_user(credentials)
        
        assert user.user_id == test_user.user_id
        assert user.username == test_user.username

    def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token."""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid")
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)
        
        assert exc_info.value.status_code == 401

    def test_get_current_user_no_sub_claim(self):
        """Test getting current user when token has no sub claim."""
        token = create_access_token({"other": "data"})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail

    def test_get_current_user_invalid_uuid(self):
        """Test getting current user with invalid UUID in token."""
        token = create_access_token({"sub": "not-a-uuid"})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)
        
        assert exc_info.value.status_code == 401
        assert "Invalid token format" in exc_info.value.detail

    def test_get_current_user_user_not_found(self):
        """Test getting current user when user doesn't exist."""
        non_existent_id = uuid4()
        token = create_access_token({"sub": str(non_existent_id)})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)
        
        assert exc_info.value.status_code == 401
        assert "User not found" in exc_info.value.detail


class TestAuthenticateUser:
    """Tests for authenticate_user function."""

    def test_authenticate_valid_credentials(self, test_user):
        """Test authenticating with valid credentials."""
        result = authenticate_user("testuser", "testpassword123")
        
        assert result is not None
        assert result.user_id == test_user.user_id
        assert result.username == "testuser"

    def test_authenticate_invalid_username(self, test_user):
        """Test authenticating with non-existent username."""
        result = authenticate_user("nonexistent", "testpassword123")
        
        assert result is None

    def test_authenticate_invalid_password(self, test_user):
        """Test authenticating with wrong password."""
        result = authenticate_user("testuser", "wrongpassword")
        
        assert result is None

    def test_authenticate_empty_username(self, test_user):
        """Test authenticating with empty username."""
        result = authenticate_user("", "testpassword123")
        
        assert result is None

    def test_authenticate_empty_password(self, test_user):
        """Test authenticating with empty password."""
        result = authenticate_user("testuser", "")
        
        assert result is None

    def test_authenticate_case_sensitive_username(self, test_user):
        """Test username is case-sensitive."""
        result = authenticate_user("TESTUSER", "testpassword123")
        
        assert result is None

    def test_authenticate_case_sensitive_password(self, test_user):
        """Test password is case-sensitive."""
        result = authenticate_user("testuser", "TESTPASSWORD123")
        
        assert result is None


class TestAuthConstants:
    """Tests for authentication constants."""

    def test_secret_key_exists(self):
        """Test SECRET_KEY is defined."""
        assert SECRET_KEY is not None
        assert len(SECRET_KEY) > 0

    def test_algorithm_is_valid(self):
        """Test ALGORITHM is a valid value."""
        assert ALGORITHM == "HS256"

    def test_token_expiry_is_reasonable(self):
        """Test ACCESS_TOKEN_EXPIRE_MINUTES is reasonable."""
        assert ACCESS_TOKEN_EXPIRE_MINUTES > 0
        assert ACCESS_TOKEN_EXPIRE_MINUTES <= 1440  # Max 24 hours
