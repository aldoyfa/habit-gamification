from dataclasses import dataclass, field
from datetime import date, datetime
from uuid import UUID, uuid4

import bcrypt


@dataclass
class Progress:
    """Value object representing habit progress"""

    completed_entries: int = 0
    total_entries: int = 0

    @property
    def percentage(self) -> int:
        if self.total_entries == 0:
            return 0
        return int((self.completed_entries / self.total_entries) * 100)

    def add_completed_entry(self) -> None:
        """Add a completed entry"""
        self.completed_entries += 1
        self.total_entries += 1

    def add_missed_entry(self) -> None:
        """Add a missed entry (only increments total)"""
        self.total_entries += 1


@dataclass
class Streak:
    """Value object representing habit streak"""

    count: int = 0

    def increment(self) -> None:
        """Increment streak count"""
        self.count += 1

    def reset(self) -> None:
        """Reset streak to zero"""
        self.count = 0


@dataclass
class HabitEntry:
    """Entity representing a single habit entry"""

    entry_id: UUID = field(default_factory=uuid4)
    date: date = field(default_factory=date.today)
    completed: bool = False


@dataclass
class Habit:
    """Aggregate root for Habit domain"""

    habit_id: UUID
    user_id: UUID
    title: str
    description: str
    progress: Progress = field(default_factory=Progress)
    streak: Streak = field(default_factory=Streak)
    entries: list[HabitEntry] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(cls, user_id: UUID, title: str, description: str) -> "Habit":
        """Factory method to create a new Habit"""
        now = datetime.now()
        return cls(
            habit_id=uuid4(),
            user_id=user_id,
            title=title,
            description=description,
            progress=Progress(),
            streak=Streak(),
            entries=[],
            created_at=now,
            updated_at=now,
        )

    def complete(self) -> None:
        """Mark habit as completed for today"""
        entry = HabitEntry(completed=True)
        self.entries.append(entry)
        self.progress.add_completed_entry()
        self.streak.increment()
        self.updated_at = datetime.now()

    def miss(self) -> None:
        """Mark habit as missed for today"""
        entry = HabitEntry(completed=False)
        self.entries.append(entry)
        self.progress.add_missed_entry()
        self.streak.reset()
        self.updated_at = datetime.now()


@dataclass
class User:
    """User entity for authentication"""

    user_id: UUID
    username: str
    hashed_password: str
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(cls, username: str, password: str) -> "User":
        """Factory method to create a new User"""
        # Hash password with bcrypt
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

        return cls(
            user_id=uuid4(),
            username=username,
            hashed_password=hashed_password,
            created_at=datetime.now(),
        )

    def verify_password(self, password: str) -> bool:
        """Verify password against hashed password"""
        return bcrypt.checkpw(password.encode("utf-8"), self.hashed_password.encode("utf-8"))
