"""
Integration tests for API routes (authentication and habit endpoints).
"""
import pytest
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app
from app.models import Habit, User
from app.repository import habit_repository, user_repository
from app.auth import create_access_token


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns welcome message."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Welcome to Habit Gamification API" in data["message"]
        assert "docs" in data
        assert "redoc" in data


class TestLoginEndpoint:
    """Tests for POST /api/auth/login endpoint."""

    def test_login_success(self, client, test_user):
        """Test successful login returns token."""
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpassword123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "accessToken" in data
        assert "tokenType" in data
        assert data["tokenType"] == "Bearer"
        assert len(data["accessToken"]) > 0

    def test_login_invalid_username(self, client, test_user):
        """Test login with invalid username returns 401."""
        response = client.post(
            "/api/auth/login",
            json={"username": "wronguser", "password": "testpassword123"}
        )
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_invalid_password(self, client, test_user):
        """Test login with invalid password returns 401."""
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "wrongpassword"}
        )
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_missing_username(self, client):
        """Test login without username returns 422."""
        response = client.post(
            "/api/auth/login",
            json={"password": "testpassword123"}
        )
        
        assert response.status_code == 422

    def test_login_missing_password(self, client):
        """Test login without password returns 422."""
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser"}
        )
        
        assert response.status_code == 422

    def test_login_empty_body(self, client):
        """Test login with empty body returns 422."""
        response = client.post("/api/auth/login", json={})
        
        assert response.status_code == 422


class TestCreateHabitEndpoint:
    """Tests for POST /api/habits endpoint."""

    def test_create_habit_success(self, client, auth_headers, test_user):
        """Test creating a habit successfully."""
        response = client.post(
            "/api/habits",
            json={
                "title": "Morning Exercise",
                "description": "30 minutes of exercise"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Morning Exercise"
        assert data["description"] == "30 minutes of exercise"
        assert data["userId"] == str(test_user.user_id)
        assert data["progress"]["completedEntries"] == 0
        assert data["streak"]["count"] == 0

    def test_create_habit_without_auth(self, client):
        """Test creating habit without authentication returns 403."""
        response = client.post(
            "/api/habits",
            json={
                "title": "Test Habit",
                "description": "Test Description"
            }
        )
        
        assert response.status_code == 403

    def test_create_habit_invalid_token(self, client):
        """Test creating habit with invalid token returns 401."""
        response = client.post(
            "/api/habits",
            json={
                "title": "Test Habit",
                "description": "Test Description"
            },
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401

    def test_create_habit_missing_title(self, client, auth_headers):
        """Test creating habit without title returns 422."""
        response = client.post(
            "/api/habits",
            json={"description": "Test Description"},
            headers=auth_headers
        )
        
        assert response.status_code == 422

    def test_create_habit_missing_description(self, client, auth_headers):
        """Test creating habit without description returns 422."""
        response = client.post(
            "/api/habits",
            json={"title": "Test Habit"},
            headers=auth_headers
        )
        
        assert response.status_code == 422

    def test_create_multiple_habits(self, client, auth_headers, test_user):
        """Test creating multiple habits."""
        response1 = client.post(
            "/api/habits",
            json={"title": "Habit 1", "description": "Desc 1"},
            headers=auth_headers
        )
        response2 = client.post(
            "/api/habits",
            json={"title": "Habit 2", "description": "Desc 2"},
            headers=auth_headers
        )
        
        assert response1.status_code == 201
        assert response2.status_code == 201
        assert response1.json()["habitId"] != response2.json()["habitId"]


class TestGetHabitEndpoint:
    """Tests for GET /api/habits/{habitId} endpoint."""

    def test_get_habit_success(self, client, auth_headers, test_habit):
        """Test getting a habit successfully."""
        response = client.get(
            f"/api/habits/{test_habit.habit_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["habitId"] == str(test_habit.habit_id)
        assert data["title"] == test_habit.title

    def test_get_habit_not_found(self, client, auth_headers):
        """Test getting non-existent habit returns 404."""
        non_existent_id = uuid4()
        response = client.get(
            f"/api/habits/{non_existent_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_get_habit_without_auth(self, client, test_habit):
        """Test getting habit without authentication returns 403."""
        response = client.get(f"/api/habits/{test_habit.habit_id}")
        
        assert response.status_code == 403

    def test_get_habit_wrong_user(self, client, auth_headers2, test_habit):
        """Test getting another user's habit returns 403."""
        response = client.get(
            f"/api/habits/{test_habit.habit_id}",
            headers=auth_headers2
        )
        
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]

    def test_get_habit_invalid_uuid(self, client, auth_headers):
        """Test getting habit with invalid UUID returns 422."""
        response = client.get(
            "/api/habits/not-a-uuid",
            headers=auth_headers
        )
        
        assert response.status_code == 422


class TestCompleteHabitEndpoint:
    """Tests for POST /api/habits/{habitId}/complete endpoint."""

    def test_complete_habit_success(self, client, auth_headers, test_habit):
        """Test completing a habit successfully."""
        response = client.post(
            f"/api/habits/{test_habit.habit_id}/complete",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["habitId"] == str(test_habit.habit_id)
        assert data["progress"]["completedEntries"] == 1
        assert data["progress"]["totalEntries"] == 1
        assert data["streak"]["count"] == 1

    def test_complete_habit_multiple_times(self, client, auth_headers, test_habit):
        """Test completing a habit multiple times."""
        for i in range(3):
            response = client.post(
                f"/api/habits/{test_habit.habit_id}/complete",
                headers=auth_headers
            )
            assert response.status_code == 200
        
        data = response.json()
        assert data["progress"]["completedEntries"] == 3
        assert data["streak"]["count"] == 3

    def test_complete_habit_not_found(self, client, auth_headers):
        """Test completing non-existent habit returns 404."""
        non_existent_id = uuid4()
        response = client.post(
            f"/api/habits/{non_existent_id}/complete",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    def test_complete_habit_without_auth(self, client, test_habit):
        """Test completing habit without authentication returns 403."""
        response = client.post(f"/api/habits/{test_habit.habit_id}/complete")
        
        assert response.status_code == 403

    def test_complete_habit_wrong_user(self, client, auth_headers2, test_habit):
        """Test completing another user's habit returns 403."""
        response = client.post(
            f"/api/habits/{test_habit.habit_id}/complete",
            headers=auth_headers2
        )
        
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]


class TestMissHabitEndpoint:
    """Tests for POST /api/habits/{habitId}/miss endpoint."""

    def test_miss_habit_success(self, client, auth_headers, test_habit):
        """Test marking a habit as missed."""
        response = client.post(
            f"/api/habits/{test_habit.habit_id}/miss",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["habitId"] == str(test_habit.habit_id)
        assert data["progress"]["completedEntries"] == 0
        assert data["progress"]["totalEntries"] == 1
        assert data["streak"]["count"] == 0

    def test_miss_habit_resets_streak(self, client, auth_headers, test_habit):
        """Test missing a habit resets the streak."""
        # Build up a streak
        for _ in range(5):
            client.post(
                f"/api/habits/{test_habit.habit_id}/complete",
                headers=auth_headers
            )
        
        # Miss the habit
        response = client.post(
            f"/api/habits/{test_habit.habit_id}/miss",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["streak"]["count"] == 0
        assert data["progress"]["completedEntries"] == 5

    def test_miss_habit_not_found(self, client, auth_headers):
        """Test missing non-existent habit returns 404."""
        non_existent_id = uuid4()
        response = client.post(
            f"/api/habits/{non_existent_id}/miss",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    def test_miss_habit_without_auth(self, client, test_habit):
        """Test missing habit without authentication returns 403."""
        response = client.post(f"/api/habits/{test_habit.habit_id}/miss")
        
        assert response.status_code == 403

    def test_miss_habit_wrong_user(self, client, auth_headers2, test_habit):
        """Test missing another user's habit returns 403."""
        response = client.post(
            f"/api/habits/{test_habit.habit_id}/miss",
            headers=auth_headers2
        )
        
        assert response.status_code == 403


class TestGetHabitProgressEndpoint:
    """Tests for GET /api/habits/{habitId}/progress endpoint."""

    def test_get_progress_success(self, client, auth_headers, test_habit):
        """Test getting habit progress successfully."""
        response = client.get(
            f"/api/habits/{test_habit.habit_id}/progress",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "progress" in data
        assert "streak" in data
        assert data["progress"]["completedEntries"] == 0
        assert data["streak"]["count"] == 0

    def test_get_progress_after_completions(self, client, auth_headers, test_habit):
        """Test getting progress after some completions."""
        # Complete habit 3 times
        for _ in range(3):
            client.post(
                f"/api/habits/{test_habit.habit_id}/complete",
                headers=auth_headers
            )
        
        response = client.get(
            f"/api/habits/{test_habit.habit_id}/progress",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["progress"]["completedEntries"] == 3
        assert data["progress"]["percentage"] == 100
        assert data["streak"]["count"] == 3

    def test_get_progress_not_found(self, client, auth_headers):
        """Test getting progress of non-existent habit returns 404."""
        non_existent_id = uuid4()
        response = client.get(
            f"/api/habits/{non_existent_id}/progress",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    def test_get_progress_without_auth(self, client, test_habit):
        """Test getting progress without authentication returns 403."""
        response = client.get(f"/api/habits/{test_habit.habit_id}/progress")
        
        assert response.status_code == 403

    def test_get_progress_wrong_user(self, client, auth_headers2, test_habit):
        """Test getting another user's habit progress returns 403."""
        response = client.get(
            f"/api/habits/{test_habit.habit_id}/progress",
            headers=auth_headers2
        )
        
        assert response.status_code == 403


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""

    def test_full_habit_workflow(self, client, test_user):
        """Test complete workflow: login -> create -> complete -> progress."""
        # Step 1: Login
        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpassword123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["accessToken"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 2: Create a habit
        create_response = client.post(
            "/api/habits",
            json={"title": "Daily Reading", "description": "Read for 30 minutes"},
            headers=headers
        )
        assert create_response.status_code == 201
        habit_id = create_response.json()["habitId"]
        
        # Step 3: Complete the habit several times
        for _ in range(7):
            client.post(f"/api/habits/{habit_id}/complete", headers=headers)
        
        # Step 4: Miss once
        client.post(f"/api/habits/{habit_id}/miss", headers=headers)
        
        # Step 5: Complete again
        for _ in range(3):
            client.post(f"/api/habits/{habit_id}/complete", headers=headers)
        
        # Step 6: Check progress
        progress_response = client.get(f"/api/habits/{habit_id}/progress", headers=headers)
        assert progress_response.status_code == 200
        
        data = progress_response.json()
        assert data["progress"]["completedEntries"] == 10
        assert data["progress"]["totalEntries"] == 11
        assert data["streak"]["count"] == 3  # Reset after miss, then 3 more

    def test_multi_user_isolation(self, client, test_user, test_user2):
        """Test that users can't access each other's habits."""
        # User 1 login and create habit
        login1 = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpassword123"}
        )
        headers1 = {"Authorization": f"Bearer {login1.json()['accessToken']}"}
        
        create_response = client.post(
            "/api/habits",
            json={"title": "User1 Habit", "description": "Private habit"},
            headers=headers1
        )
        habit_id = create_response.json()["habitId"]
        
        # User 2 login
        login2 = client.post(
            "/api/auth/login",
            json={"username": "testuser2", "password": "testpassword456"}
        )
        headers2 = {"Authorization": f"Bearer {login2.json()['accessToken']}"}
        
        # User 2 tries to access User 1's habit
        get_response = client.get(f"/api/habits/{habit_id}", headers=headers2)
        assert get_response.status_code == 403
        
        complete_response = client.post(f"/api/habits/{habit_id}/complete", headers=headers2)
        assert complete_response.status_code == 403
        
        miss_response = client.post(f"/api/habits/{habit_id}/miss", headers=headers2)
        assert miss_response.status_code == 403
        
        progress_response = client.get(f"/api/habits/{habit_id}/progress", headers=headers2)
        assert progress_response.status_code == 403
