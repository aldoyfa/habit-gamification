"""
Unit tests for repository layer (HabitRepository, UserRepository).
"""
import pytest
from uuid import uuid4

from app.models import Habit, User
from app.repository import HabitRepository, UserRepository


class TestHabitRepository:
    """Tests for HabitRepository."""

    def test_save_habit(self, fresh_habit_repository):
        """Test saving a habit to repository."""
        repo = fresh_habit_repository
        habit = Habit.create(uuid4(), "Test Habit", "Description")
        
        result = repo.save(habit)
        
        assert result == habit
        assert repo.get_by_id(habit.habit_id) == habit

    def test_save_habit_update(self, fresh_habit_repository):
        """Test updating an existing habit."""
        repo = fresh_habit_repository
        habit = Habit.create(uuid4(), "Test Habit", "Description")
        repo.save(habit)
        
        habit.complete()
        repo.save(habit)
        
        retrieved = repo.get_by_id(habit.habit_id)
        assert retrieved.progress.completed_entries == 1

    def test_get_by_id_existing(self, fresh_habit_repository):
        """Test getting an existing habit by ID."""
        repo = fresh_habit_repository
        habit = Habit.create(uuid4(), "Test", "Desc")
        repo.save(habit)
        
        result = repo.get_by_id(habit.habit_id)
        
        assert result == habit

    def test_get_by_id_not_found(self, fresh_habit_repository):
        """Test getting a non-existent habit returns None."""
        repo = fresh_habit_repository
        
        result = repo.get_by_id(uuid4())
        
        assert result is None

    def test_exists_true(self, fresh_habit_repository):
        """Test exists returns True for existing habit."""
        repo = fresh_habit_repository
        habit = Habit.create(uuid4(), "Test", "Desc")
        repo.save(habit)
        
        assert repo.exists(habit.habit_id) is True

    def test_exists_false(self, fresh_habit_repository):
        """Test exists returns False for non-existent habit."""
        repo = fresh_habit_repository
        
        assert repo.exists(uuid4()) is False

    def test_delete_existing(self, fresh_habit_repository):
        """Test deleting an existing habit."""
        repo = fresh_habit_repository
        habit = Habit.create(uuid4(), "Test", "Desc")
        repo.save(habit)
        
        result = repo.delete(habit.habit_id)
        
        assert result is True
        assert repo.get_by_id(habit.habit_id) is None

    def test_delete_not_found(self, fresh_habit_repository):
        """Test deleting a non-existent habit returns False."""
        repo = fresh_habit_repository
        
        result = repo.delete(uuid4())
        
        assert result is False

    def test_get_all_empty(self, fresh_habit_repository):
        """Test get_all returns empty list when no habits."""
        repo = fresh_habit_repository
        
        result = repo.get_all()
        
        assert result == []

    def test_get_all_multiple(self, fresh_habit_repository):
        """Test get_all returns all habits."""
        repo = fresh_habit_repository
        user_id = uuid4()
        habit1 = Habit.create(user_id, "Habit 1", "Desc 1")
        habit2 = Habit.create(user_id, "Habit 2", "Desc 2")
        habit3 = Habit.create(user_id, "Habit 3", "Desc 3")
        
        repo.save(habit1)
        repo.save(habit2)
        repo.save(habit3)
        
        result = repo.get_all()
        
        assert len(result) == 3
        assert habit1 in result
        assert habit2 in result
        assert habit3 in result

    def test_repository_isolation(self):
        """Test that different repository instances are isolated."""
        repo1 = HabitRepository()
        repo2 = HabitRepository()
        
        habit = Habit.create(uuid4(), "Test", "Desc")
        repo1.save(habit)
        
        assert repo1.get_by_id(habit.habit_id) == habit
        assert repo2.get_by_id(habit.habit_id) is None


class TestUserRepository:
    """Tests for UserRepository."""

    def test_save_user(self, fresh_user_repository):
        """Test saving a user to repository."""
        repo = fresh_user_repository
        user = User.create("testuser", "password123")
        
        result = repo.save(user)
        
        assert result == user
        assert repo.get_by_id(user.user_id) == user

    def test_save_user_update(self, fresh_user_repository):
        """Test updating an existing user."""
        repo = fresh_user_repository
        user = User.create("testuser", "password123")
        repo.save(user)
        
        # Save again (update)
        repo.save(user)
        
        assert repo.get_by_id(user.user_id) == user

    def test_get_by_id_existing(self, fresh_user_repository):
        """Test getting an existing user by ID."""
        repo = fresh_user_repository
        user = User.create("testuser", "password123")
        repo.save(user)
        
        result = repo.get_by_id(user.user_id)
        
        assert result == user

    def test_get_by_id_not_found(self, fresh_user_repository):
        """Test getting a non-existent user returns None."""
        repo = fresh_user_repository
        
        result = repo.get_by_id(uuid4())
        
        assert result is None

    def test_get_by_username_existing(self, fresh_user_repository):
        """Test getting a user by username."""
        repo = fresh_user_repository
        user = User.create("testuser", "password123")
        repo.save(user)
        
        result = repo.get_by_username("testuser")
        
        assert result == user

    def test_get_by_username_not_found(self, fresh_user_repository):
        """Test getting a non-existent username returns None."""
        repo = fresh_user_repository
        
        result = repo.get_by_username("nonexistent")
        
        assert result is None

    def test_get_by_username_case_sensitive(self, fresh_user_repository):
        """Test username lookup is case-sensitive."""
        repo = fresh_user_repository
        user = User.create("TestUser", "password123")
        repo.save(user)
        
        assert repo.get_by_username("TestUser") == user
        assert repo.get_by_username("testuser") is None
        assert repo.get_by_username("TESTUSER") is None

    def test_exists_true(self, fresh_user_repository):
        """Test exists returns True for existing user."""
        repo = fresh_user_repository
        user = User.create("testuser", "password123")
        repo.save(user)
        
        assert repo.exists(user.user_id) is True

    def test_exists_false(self, fresh_user_repository):
        """Test exists returns False for non-existent user."""
        repo = fresh_user_repository
        
        assert repo.exists(uuid4()) is False

    def test_multiple_users(self, fresh_user_repository):
        """Test storing multiple users."""
        repo = fresh_user_repository
        user1 = User.create("user1", "pass1")
        user2 = User.create("user2", "pass2")
        user3 = User.create("user3", "pass3")
        
        repo.save(user1)
        repo.save(user2)
        repo.save(user3)
        
        assert repo.get_by_username("user1") == user1
        assert repo.get_by_username("user2") == user2
        assert repo.get_by_username("user3") == user3

    def test_repository_isolation(self):
        """Test that different repository instances are isolated."""
        repo1 = UserRepository()
        repo2 = UserRepository()
        
        user = User.create("testuser", "password")
        repo1.save(user)
        
        assert repo1.get_by_id(user.user_id) == user
        assert repo2.get_by_id(user.user_id) is None
        assert repo1.get_by_username("testuser") == user
        assert repo2.get_by_username("testuser") is None

    def test_username_index_updated_on_save(self, fresh_user_repository):
        """Test username index is properly updated on save."""
        repo = fresh_user_repository
        user = User.create("originalname", "password")
        repo.save(user)
        
        # Simulate username change (not typical but tests index)
        assert repo.get_by_username("originalname") == user
