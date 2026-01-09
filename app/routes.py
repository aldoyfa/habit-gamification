from fastapi import APIRouter, HTTPException, status
from uuid import UUID

from app.schemas import (
    CreateHabitRequest,
    HabitResponse,
    HabitCompletionResponse,
    ProgressResponse,
    ProgressSchema,
    StreakSchema,
)
from app.models import Habit
from app.repository import habit_repository

router = APIRouter(prefix="/api/habits", tags=["Habits"])


def habit_to_response(habit: Habit) -> HabitResponse:
    """Convert domain Habit to HabitResponse schema"""
    return HabitResponse(
        habitId=habit.habit_id,
        userId=habit.user_id,
        title=habit.title,
        description=habit.description,
        progress=ProgressSchema(
            completedEntries=habit.progress.completed_entries,
            totalEntries=habit.progress.total_entries,
            percentage=habit.progress.percentage,
        ),
        streak=StreakSchema(count=habit.streak.count),
        created_at=habit.created_at,
        updated_at=habit.updated_at,
    )


def habit_to_completion_response(habit: Habit) -> HabitCompletionResponse:
    """Convert domain Habit to HabitCompletionResponse schema"""
    return HabitCompletionResponse(
        habitId=habit.habit_id,
        progress=ProgressSchema(
            completedEntries=habit.progress.completed_entries,
            totalEntries=habit.progress.total_entries,
            percentage=habit.progress.percentage,
        ),
        streak=StreakSchema(count=habit.streak.count),
    )


def habit_to_progress_response(habit: Habit) -> ProgressResponse:
    """Convert domain Habit to ProgressResponse schema"""
    return ProgressResponse(
        progress=ProgressSchema(
            completedEntries=habit.progress.completed_entries,
            totalEntries=habit.progress.total_entries,
            percentage=habit.progress.percentage,
        ),
        streak=StreakSchema(count=habit.streak.count),
    )


@router.post(
    "",
    response_model=HabitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new habit",
    description="Membuat objek Habit baru sebagai aggregate root dan menginisialisasi komponen internalnya.",
)
def create_habit(request: CreateHabitRequest) -> HabitResponse:
    """
    Create a new habit with the given details.
    
    - **userId**: UUID of the user who owns the habit
    - **title**: Title of the habit
    - **description**: Description of the habit
    """
    habit = Habit.create(
        user_id=request.userId,
        title=request.title,
        description=request.description,
    )
    habit_repository.save(habit)
    return habit_to_response(habit)


@router.get(
    "/{habitId}",
    response_model=HabitResponse,
    summary="Get habit by ID",
    description="Mengambil representasi state terkini dari sebuah Habit, termasuk progres dan streak.",
)
def get_habit(habitId: UUID) -> HabitResponse:
    """
    Get the current state of a habit including progress and streak.
    
    - **habitId**: UUID of the habit to retrieve
    """
    habit = habit_repository.get_by_id(habitId)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habit with id {habitId} not found",
        )
    return habit_to_response(habit)


@router.post(
    "/{habitId}/complete",
    response_model=HabitCompletionResponse,
    summary="Complete habit for today",
    description="Mencatat penyelesaian habit pada hari berjalan dengan menambahkan HabitEntry dan memperbarui Progress serta Streak.",
)
def complete_habit(habitId: UUID) -> HabitCompletionResponse:
    """
    Record habit completion for the current day.
    
    - **habitId**: UUID of the habit to mark as completed
    """
    habit = habit_repository.get_by_id(habitId)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habit with id {habitId} not found",
        )
    habit.complete()
    habit_repository.save(habit)
    return habit_to_completion_response(habit)


@router.post(
    "/{habitId}/miss",
    response_model=HabitCompletionResponse,
    summary="Miss habit for today",
    description="Mencatat kegagalan penyelesaian habit pada hari berjalan dan memperbarui nilai streak sesuai aturan domain.",
)
def miss_habit(habitId: UUID) -> HabitCompletionResponse:
    """
    Record habit miss for the current day.
    
    - **habitId**: UUID of the habit to mark as missed
    """
    habit = habit_repository.get_by_id(habitId)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habit with id {habitId} not found",
        )
    habit.miss()
    habit_repository.save(habit)
    return habit_to_completion_response(habit)


@router.get(
    "/{habitId}/progress",
    response_model=ProgressResponse,
    summary="Get habit progress",
    description="Mengambil ringkasan value object Progress dan Streak tanpa memuat detail atribut lain dari Habit.",
)
def get_habit_progress(habitId: UUID) -> ProgressResponse:
    """
    Get progress and streak summary for a habit.
    
    - **habitId**: UUID of the habit to get progress for
    """
    habit = habit_repository.get_by_id(habitId)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habit with id {habitId} not found",
        )
    return habit_to_progress_response(habit)
