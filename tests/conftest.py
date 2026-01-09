"""
Pytest configuration and fixtures for testing.
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.models import User, Habit
from app.repository import habit_repository, user_repository, HabitRepository, UserRepository
from app.auth import create_access_token


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_repositories():
    """Reset repositories before each test to ensure isolation."""
    # Clear habit repository
    habit_repository._habits.clear()
    # Clear user repository
    user_repository._users.clear()
    user_repository._username_index.clear()
    yield
    # Cleanup after test
    habit_repository._habits.clear()
    user_repository._users.clear()
    user_repository._username_index.clear()


@pytest.fixture
def test_user():
    """Create and return a test user."""
    user = User.create(username="testuser", password="testpassword123")
    user_repository.save(user)
    return user


@pytest.fixture
def test_user2():
    """Create and return a second test user for authorization tests."""
    user = User.create(username="testuser2", password="testpassword456")
    user_repository.save(user)
    return user


@pytest.fixture
def auth_token(test_user):
    """Generate a valid authentication token for the test user."""
    return create_access_token(data={"sub": str(test_user.user_id)})


@pytest.fixture
def auth_token2(test_user2):
    """Generate a valid authentication token for the second test user."""
    return create_access_token(data={"sub": str(test_user2.user_id)})


@pytest.fixture
def auth_headers(auth_token):
    """Return headers with authentication token."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def auth_headers2(auth_token2):
    """Return headers with authentication token for second user."""
    return {"Authorization": f"Bearer {auth_token2}"}


@pytest.fixture
def test_habit(test_user):
    """Create and return a test habit."""
    habit = Habit.create(
        user_id=test_user.user_id,
        title="Test Habit",
        description="Test Description"
    )
    habit_repository.save(habit)
    return habit


@pytest.fixture
def fresh_habit_repository():
    """Create a fresh habit repository instance for isolated testing."""
    return HabitRepository()


@pytest.fixture
def fresh_user_repository():
    """Create a fresh user repository instance for isolated testing."""
    return UserRepository()
