"""
Unit tests for Pydantic schemas (request/response validation).
"""

from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas import (
    CreateHabitRequest,
    HabitCompletionResponse,
    HabitResponse,
    LoginRequest,
    ProgressResponse,
    ProgressSchema,
    StreakSchema,
    TokenResponse,
)


class TestProgressSchema:
    """Tests for ProgressSchema."""

    def test_progress_schema_default_values(self):
        """Test ProgressSchema with default values."""
        progress = ProgressSchema()
        assert progress.completedEntries == 0
        assert progress.totalEntries == 0
        assert progress.percentage == 0

    def test_progress_schema_custom_values(self):
        """Test ProgressSchema with custom values."""
        progress = ProgressSchema(completedEntries=5, totalEntries=10, percentage=50)
        assert progress.completedEntries == 5
        assert progress.totalEntries == 10
        assert progress.percentage == 50

    def test_progress_schema_serialization(self):
        """Test ProgressSchema serializes to dict correctly."""
        progress = ProgressSchema(completedEntries=3, totalEntries=5, percentage=60)
        data = progress.model_dump()
        assert data == {"completedEntries": 3, "totalEntries": 5, "percentage": 60}

    def test_progress_schema_from_dict(self):
        """Test ProgressSchema can be created from dict."""
        data = {"completedEntries": 7, "totalEntries": 10, "percentage": 70}
        progress = ProgressSchema(**data)
        assert progress.completedEntries == 7


class TestStreakSchema:
    """Tests for StreakSchema."""

    def test_streak_schema_default_value(self):
        """Test StreakSchema with default value."""
        streak = StreakSchema()
        assert streak.count == 0

    def test_streak_schema_custom_value(self):
        """Test StreakSchema with custom value."""
        streak = StreakSchema(count=15)
        assert streak.count == 15

    def test_streak_schema_serialization(self):
        """Test StreakSchema serializes correctly."""
        streak = StreakSchema(count=5)
        assert streak.model_dump() == {"count": 5}


class TestCreateHabitRequest:
    """Tests for CreateHabitRequest schema."""

    def test_create_habit_request_valid(self):
        """Test valid CreateHabitRequest."""
        request = CreateHabitRequest(title="Morning Exercise", description="30 minutes of exercise")
        assert request.title == "Morning Exercise"
        assert request.description == "30 minutes of exercise"

    def test_create_habit_request_missing_title(self):
        """Test CreateHabitRequest without title raises error."""
        with pytest.raises(ValidationError):
            CreateHabitRequest(description="Description only")

    def test_create_habit_request_missing_description(self):
        """Test CreateHabitRequest without description raises error."""
        with pytest.raises(ValidationError):
            CreateHabitRequest(title="Title only")

    def test_create_habit_request_empty_title(self):
        """Test CreateHabitRequest with empty title is valid (schema allows it)."""
        request = CreateHabitRequest(title="", description="Description")
        assert request.title == ""

    def test_create_habit_request_serialization(self):
        """Test CreateHabitRequest serializes correctly."""
        request = CreateHabitRequest(title="Test", description="Desc")
        data = request.model_dump()
        assert data == {"title": "Test", "description": "Desc"}


class TestHabitResponse:
    """Tests for HabitResponse schema."""

    def test_habit_response_valid(self):
        """Test valid HabitResponse."""
        habit_id = uuid4()
        user_id = uuid4()
        now = datetime.now()

        response = HabitResponse(
            habitId=habit_id,
            userId=user_id,
            title="Test Habit",
            description="Test Description",
            progress=ProgressSchema(completedEntries=5, totalEntries=10, percentage=50),
            streak=StreakSchema(count=3),
            created_at=now,
            updated_at=now,
        )

        assert response.habitId == habit_id
        assert response.userId == user_id
        assert response.title == "Test Habit"
        assert response.progress.completedEntries == 5
        assert response.streak.count == 3

    def test_habit_response_missing_fields(self):
        """Test HabitResponse with missing required fields raises error."""
        with pytest.raises(ValidationError):
            HabitResponse(
                habitId=uuid4(),
                title="Test",
                # Missing other required fields
            )

    def test_habit_response_serialization(self):
        """Test HabitResponse serializes to JSON-compatible format."""
        habit_id = uuid4()
        user_id = uuid4()
        now = datetime.now()

        response = HabitResponse(
            habitId=habit_id,
            userId=user_id,
            title="Test",
            description="Desc",
            progress=ProgressSchema(),
            streak=StreakSchema(),
            created_at=now,
            updated_at=now,
        )

        data = response.model_dump()
        assert data["habitId"] == habit_id
        assert data["userId"] == user_id


class TestHabitCompletionResponse:
    """Tests for HabitCompletionResponse schema."""

    def test_habit_completion_response_valid(self):
        """Test valid HabitCompletionResponse."""
        habit_id = uuid4()

        response = HabitCompletionResponse(
            habitId=habit_id,
            progress=ProgressSchema(completedEntries=10, totalEntries=12, percentage=83),
            streak=StreakSchema(count=5),
        )

        assert response.habitId == habit_id
        assert response.progress.completedEntries == 10
        assert response.streak.count == 5

    def test_habit_completion_response_missing_fields(self):
        """Test HabitCompletionResponse with missing fields raises error."""
        with pytest.raises(ValidationError):
            HabitCompletionResponse(habitId=uuid4())


class TestProgressResponse:
    """Tests for ProgressResponse schema."""

    def test_progress_response_valid(self):
        """Test valid ProgressResponse."""
        response = ProgressResponse(
            progress=ProgressSchema(completedEntries=8, totalEntries=10, percentage=80),
            streak=StreakSchema(count=4),
        )

        assert response.progress.percentage == 80
        assert response.streak.count == 4

    def test_progress_response_serialization(self):
        """Test ProgressResponse serializes correctly."""
        response = ProgressResponse(
            progress=ProgressSchema(completedEntries=5, totalEntries=5, percentage=100),
            streak=StreakSchema(count=5),
        )

        data = response.model_dump()
        assert data["progress"]["percentage"] == 100
        assert data["streak"]["count"] == 5


class TestLoginRequest:
    """Tests for LoginRequest schema."""

    def test_login_request_valid(self):
        """Test valid LoginRequest."""
        request = LoginRequest(username="testuser", password="testpass123")
        assert request.username == "testuser"
        assert request.password == "testpass123"

    def test_login_request_missing_username(self):
        """Test LoginRequest without username raises error."""
        with pytest.raises(ValidationError):
            LoginRequest(password="testpass123")

    def test_login_request_missing_password(self):
        """Test LoginRequest without password raises error."""
        with pytest.raises(ValidationError):
            LoginRequest(username="testuser")

    def test_login_request_empty_values(self):
        """Test LoginRequest with empty values is valid (schema allows it)."""
        request = LoginRequest(username="", password="")
        assert request.username == ""
        assert request.password == ""

    def test_login_request_serialization(self):
        """Test LoginRequest serializes correctly."""
        request = LoginRequest(username="user", password="pass")
        data = request.model_dump()
        assert data == {"username": "user", "password": "pass"}


class TestTokenResponse:
    """Tests for TokenResponse schema."""

    def test_token_response_valid(self):
        """Test valid TokenResponse."""
        response = TokenResponse(accessToken="jwt.token.here", tokenType="Bearer")
        assert response.accessToken == "jwt.token.here"
        assert response.tokenType == "Bearer"

    def test_token_response_default_token_type(self):
        """Test TokenResponse uses default tokenType."""
        response = TokenResponse(accessToken="jwt.token.here")
        assert response.tokenType == "Bearer"

    def test_token_response_missing_access_token(self):
        """Test TokenResponse without accessToken raises error."""
        with pytest.raises(ValidationError):
            TokenResponse(tokenType="Bearer")

    def test_token_response_serialization(self):
        """Test TokenResponse serializes correctly."""
        response = TokenResponse(accessToken="token123", tokenType="Bearer")
        data = response.model_dump()
        assert data == {"accessToken": "token123", "tokenType": "Bearer"}
