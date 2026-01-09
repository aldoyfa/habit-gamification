"""
Unit tests for domain models (Progress, Streak, HabitEntry, Habit, User).
"""

from datetime import date, datetime
from uuid import UUID, uuid4

from app.models import Habit, HabitEntry, Progress, Streak, User


class TestProgress:
    """Tests for Progress value object."""

    def test_progress_default_values(self):
        """Test Progress is created with default values."""
        progress = Progress()
        assert progress.completed_entries == 0
        assert progress.total_entries == 0

    def test_progress_custom_values(self):
        """Test Progress can be created with custom values."""
        progress = Progress(completed_entries=5, total_entries=10)
        assert progress.completed_entries == 5
        assert progress.total_entries == 10

    def test_percentage_with_zero_total(self):
        """Test percentage returns 0 when total_entries is 0."""
        progress = Progress()
        assert progress.percentage == 0

    def test_percentage_calculation(self):
        """Test percentage is calculated correctly."""
        progress = Progress(completed_entries=7, total_entries=10)
        assert progress.percentage == 70

    def test_percentage_rounds_down(self):
        """Test percentage rounds down to integer."""
        progress = Progress(completed_entries=1, total_entries=3)
        assert progress.percentage == 33  # 33.33... rounds to 33

    def test_percentage_full_completion(self):
        """Test percentage is 100 when all entries completed."""
        progress = Progress(completed_entries=10, total_entries=10)
        assert progress.percentage == 100

    def test_add_completed_entry(self):
        """Test adding a completed entry increments both counters."""
        progress = Progress()
        progress.add_completed_entry()
        assert progress.completed_entries == 1
        assert progress.total_entries == 1

    def test_add_completed_entry_multiple(self):
        """Test adding multiple completed entries."""
        progress = Progress()
        progress.add_completed_entry()
        progress.add_completed_entry()
        progress.add_completed_entry()
        assert progress.completed_entries == 3
        assert progress.total_entries == 3

    def test_add_missed_entry(self):
        """Test adding a missed entry only increments total."""
        progress = Progress()
        progress.add_missed_entry()
        assert progress.completed_entries == 0
        assert progress.total_entries == 1

    def test_add_missed_entry_multiple(self):
        """Test adding multiple missed entries."""
        progress = Progress()
        progress.add_missed_entry()
        progress.add_missed_entry()
        assert progress.completed_entries == 0
        assert progress.total_entries == 2

    def test_mixed_entries(self):
        """Test mix of completed and missed entries."""
        progress = Progress()
        progress.add_completed_entry()
        progress.add_missed_entry()
        progress.add_completed_entry()
        progress.add_missed_entry()
        assert progress.completed_entries == 2
        assert progress.total_entries == 4
        assert progress.percentage == 50


class TestStreak:
    """Tests for Streak value object."""

    def test_streak_default_value(self):
        """Test Streak is created with default count of 0."""
        streak = Streak()
        assert streak.count == 0

    def test_streak_custom_value(self):
        """Test Streak can be created with custom value."""
        streak = Streak(count=5)
        assert streak.count == 5

    def test_increment(self):
        """Test incrementing streak count."""
        streak = Streak()
        streak.increment()
        assert streak.count == 1

    def test_increment_multiple(self):
        """Test incrementing streak multiple times."""
        streak = Streak()
        streak.increment()
        streak.increment()
        streak.increment()
        assert streak.count == 3

    def test_reset(self):
        """Test resetting streak to zero."""
        streak = Streak(count=10)
        streak.reset()
        assert streak.count == 0

    def test_reset_already_zero(self):
        """Test resetting a streak that's already zero."""
        streak = Streak()
        streak.reset()
        assert streak.count == 0

    def test_increment_after_reset(self):
        """Test incrementing after reset starts from 1."""
        streak = Streak(count=5)
        streak.reset()
        streak.increment()
        assert streak.count == 1


class TestHabitEntry:
    """Tests for HabitEntry entity."""

    def test_habit_entry_default_values(self):
        """Test HabitEntry is created with default values."""
        entry = HabitEntry()
        assert isinstance(entry.entry_id, UUID)
        assert entry.date == date.today()
        assert entry.completed is False

    def test_habit_entry_completed(self):
        """Test HabitEntry can be created as completed."""
        entry = HabitEntry(completed=True)
        assert entry.completed is True

    def test_habit_entry_custom_date(self):
        """Test HabitEntry with custom date."""
        custom_date = date(2026, 1, 1)
        entry = HabitEntry(date=custom_date)
        assert entry.date == custom_date

    def test_habit_entry_unique_ids(self):
        """Test each HabitEntry gets a unique ID."""
        entry1 = HabitEntry()
        entry2 = HabitEntry()
        assert entry1.entry_id != entry2.entry_id


class TestHabit:
    """Tests for Habit aggregate root."""

    def test_habit_create_factory(self):
        """Test Habit.create factory method."""
        user_id = uuid4()
        habit = Habit.create(user_id=user_id, title="Test Habit", description="Test Description")

        assert isinstance(habit.habit_id, UUID)
        assert habit.user_id == user_id
        assert habit.title == "Test Habit"
        assert habit.description == "Test Description"
        assert habit.progress.completed_entries == 0
        assert habit.streak.count == 0
        assert habit.entries == []
        assert isinstance(habit.created_at, datetime)
        assert isinstance(habit.updated_at, datetime)

    def test_habit_create_unique_ids(self):
        """Test each Habit gets a unique ID."""
        user_id = uuid4()
        habit1 = Habit.create(user_id, "Habit 1", "Desc 1")
        habit2 = Habit.create(user_id, "Habit 2", "Desc 2")
        assert habit1.habit_id != habit2.habit_id

    def test_habit_complete(self):
        """Test completing a habit."""
        habit = Habit.create(uuid4(), "Test", "Test")
        original_updated_at = habit.updated_at

        habit.complete()

        assert len(habit.entries) == 1
        assert habit.entries[0].completed is True
        assert habit.progress.completed_entries == 1
        assert habit.progress.total_entries == 1
        assert habit.streak.count == 1
        assert habit.updated_at >= original_updated_at

    def test_habit_complete_multiple(self):
        """Test completing a habit multiple times."""
        habit = Habit.create(uuid4(), "Test", "Test")

        habit.complete()
        habit.complete()
        habit.complete()

        assert len(habit.entries) == 3
        assert habit.progress.completed_entries == 3
        assert habit.progress.total_entries == 3
        assert habit.streak.count == 3

    def test_habit_miss(self):
        """Test missing a habit."""
        habit = Habit.create(uuid4(), "Test", "Test")
        original_updated_at = habit.updated_at

        habit.miss()

        assert len(habit.entries) == 1
        assert habit.entries[0].completed is False
        assert habit.progress.completed_entries == 0
        assert habit.progress.total_entries == 1
        assert habit.streak.count == 0
        assert habit.updated_at >= original_updated_at

    def test_habit_miss_resets_streak(self):
        """Test missing a habit resets the streak."""
        habit = Habit.create(uuid4(), "Test", "Test")

        habit.complete()
        habit.complete()
        habit.complete()
        assert habit.streak.count == 3

        habit.miss()
        assert habit.streak.count == 0

    def test_habit_complete_after_miss(self):
        """Test completing after a miss starts new streak."""
        habit = Habit.create(uuid4(), "Test", "Test")

        habit.complete()
        habit.complete()
        habit.miss()
        habit.complete()

        assert habit.streak.count == 1
        assert habit.progress.completed_entries == 3
        assert habit.progress.total_entries == 4


class TestUser:
    """Tests for User entity."""

    def test_user_create_factory(self):
        """Test User.create factory method."""
        user = User.create(username="testuser", password="testpass123")

        assert isinstance(user.user_id, UUID)
        assert user.username == "testuser"
        assert user.hashed_password != "testpass123"  # Password should be hashed
        assert isinstance(user.created_at, datetime)

    def test_user_create_unique_ids(self):
        """Test each User gets a unique ID."""
        user1 = User.create("user1", "pass1")
        user2 = User.create("user2", "pass2")
        assert user1.user_id != user2.user_id

    def test_user_password_hashing(self):
        """Test password is hashed differently each time (salt)."""
        user1 = User.create("user1", "samepassword")
        user2 = User.create("user2", "samepassword")
        assert user1.hashed_password != user2.hashed_password

    def test_verify_password_correct(self):
        """Test verify_password returns True for correct password."""
        user = User.create("testuser", "correctpassword")
        assert user.verify_password("correctpassword") is True

    def test_verify_password_incorrect(self):
        """Test verify_password returns False for incorrect password."""
        user = User.create("testuser", "correctpassword")
        assert user.verify_password("wrongpassword") is False

    def test_verify_password_empty(self):
        """Test verify_password returns False for empty password."""
        user = User.create("testuser", "correctpassword")
        assert user.verify_password("") is False

    def test_verify_password_similar(self):
        """Test verify_password returns False for similar but different password."""
        user = User.create("testuser", "password123")
        assert user.verify_password("password124") is False
        assert user.verify_password("Password123") is False
        assert user.verify_password(" password123") is False
