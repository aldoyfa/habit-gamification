from uuid import UUID

from app.models import Habit, User


class HabitRepository:
    """In-memory repository for Habit aggregate"""

    def __init__(self):
        self._habits: dict[UUID, Habit] = {}

    def save(self, habit: Habit) -> Habit:
        """Save a habit to the repository"""
        self._habits[habit.habit_id] = habit
        return habit

    def get_by_id(self, habit_id: UUID) -> Habit | None:
        """Get a habit by its ID"""
        return self._habits.get(habit_id)

    def exists(self, habit_id: UUID) -> bool:
        """Check if a habit exists"""
        return habit_id in self._habits

    def delete(self, habit_id: UUID) -> bool:
        """Delete a habit by its ID"""
        if habit_id in self._habits:
            del self._habits[habit_id]
            return True
        return False

    def get_all(self) -> list[Habit]:
        """Get all habits"""
        return list(self._habits.values())


# Singleton instance for the repository
habit_repository = HabitRepository()


class UserRepository:
    """In-memory repository for User entity"""

    def __init__(self):
        self._users: dict[UUID, User] = {}
        self._username_index: dict[str, UUID] = {}

    def save(self, user: User) -> User:
        """Save a user to the repository"""
        self._users[user.user_id] = user
        self._username_index[user.username] = user.user_id
        return user

    def get_by_id(self, user_id: UUID) -> User | None:
        """Get a user by their ID"""
        return self._users.get(user_id)

    def get_by_username(self, username: str) -> User | None:
        """Get a user by their username"""
        user_id = self._username_index.get(username)
        if user_id:
            return self._users.get(user_id)
        return None

    def exists(self, user_id: UUID) -> bool:
        """Check if a user exists"""
        return user_id in self._users


# Singleton instance for the user repository
user_repository = UserRepository()
