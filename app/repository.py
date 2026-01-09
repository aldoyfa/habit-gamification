from uuid import UUID
from typing import Dict, Optional
from app.models import Habit


class HabitRepository:
    """In-memory repository for Habit aggregate"""

    def __init__(self):
        self._habits: Dict[UUID, Habit] = {}

    def save(self, habit: Habit) -> Habit:
        """Save a habit to the repository"""
        self._habits[habit.habit_id] = habit
        return habit

    def get_by_id(self, habit_id: UUID) -> Optional[Habit]:
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
