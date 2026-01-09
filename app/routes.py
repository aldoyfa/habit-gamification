from fastapi import APIRouter, HTTPException, status, Depends
from uuid import UUID
from datetime import timedelta

from app.schemas import (
    CreateHabitRequest,
    HabitResponse,
    HabitCompletionResponse,
    ProgressResponse,
    ProgressSchema,
    StreakSchema,
    LoginRequest,
    TokenResponse,
)
from app.models import Habit, User
from app.repository import habit_repository, user_repository
from app.auth import authenticate_user, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/api", tags=["API"])
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
habits_router = APIRouter(prefix="/habits", tags=["Habits"])


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


# Authentication Endpoints
@auth_router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Melakukan proses autentikasi pengguna dan menghasilkan JWT apabila kredensial valid.",
)
def login(request: LoginRequest) -> TokenResponse:
    """
    Authenticate user and return JWT access token.
    
    - **username**: Username for authentication
    - **password**: Password for authentication
    """
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.user_id)},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(accessToken=access_token, tokenType="Bearer")


# Habit Endpoints (Protected)
@habits_router.post(
    "",
    response_model=HabitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new habit",
    description="Membuat objek Habit baru sebagai aggregate root dan menginisialisasi komponen internalnya.",
)
def create_habit(request: CreateHabitRequest, current_user: User = Depends(get_current_user)) -> HabitResponse:
    """
    Create a new habit with the given details.
    
    - **userId**: UUID of the user who owns the habit
    - **title**: Title of the habit
    - **description**: Description of the habit
    
    Requires: Valid JWT token in Authorization header
    """
    # Use authenticated user's ID instead of request userId
    habit = Habit.create(
        user_id=current_user.user_id,
        title=request.title,
        description=request.description,
    )
    habit_repository.save(habit)
    return habit_to_response(habit)


@habits_router.get(
    "/{habitId}",
    response_model=HabitResponse,
    summary="Get habit by ID",
    description="Mengambil representasi state terkini dari sebuah Habit, termasuk progres dan streak.",
)
def get_habit(habitId: UUID, current_user: User = Depends(get_current_user)) -> HabitResponse:
    """
    Get the current state of a habit including progress and streak.
    
    - **habitId**: UUID of the habit to retrieve
    
    Requires: Valid JWT token in Authorization header
    """
    habit = habit_repository.get_by_id(habitId)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habit with id {habitId} not found",
        )
    
    # Ensure user can only access their own habits
    if habit.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this habit",
        )
    
    return habit_to_response(habit)


@habits_router.post(
    "/{habitId}/complete",
    response_model=HabitCompletionResponse,
    summary="Complete habit for today",
    description="Mencatat penyelesaian habit pada hari berjalan dengan menambahkan HabitEntry dan memperbarui Progress serta Streak.",
)
def complete_habit(habitId: UUID, current_user: User = Depends(get_current_user)) -> HabitCompletionResponse:
    """
    Record habit completion for the current day.
    
    - **habitId**: UUID of the habit to mark as completed
    
    Requires: Valid JWT token in Authorization header
    """
    habit = habit_repository.get_by_id(habitId)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habit with id {habitId} not found",
        )
    
    # Ensure user can only complete their own habits
    if habit.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this habit",
        )
    
    habit.complete()
    habit_repository.save(habit)
    return habit_to_completion_response(habit)


@habits_router.post(
    "/{habitId}/miss",
    response_model=HabitCompletionResponse,
    summary="Miss habit for today",
    description="Mencatat kegagalan penyelesaian habit pada hari berjalan dan memperbarui nilai streak sesuai aturan domain.",
)
def miss_habit(habitId: UUID, current_user: User = Depends(get_current_user)) -> HabitCompletionResponse:
    """
    Record habit miss for the current day.
    
    - **habitId**: UUID of the habit to mark as missed
    
    Requires: Valid JWT token in Authorization header
    """
    habit = habit_repository.get_by_id(habitId)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habit with id {habitId} not found",
        )
    
    # Ensure user can only modify their own habits
    if habit.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this habit",
        )
    
    habit.miss()
    habit_repository.save(habit)
    return habit_to_completion_response(habit)


@habits_router.get(
    "/{habitId}/progress",
    response_model=ProgressResponse,
    summary="Get habit progress",
    description="Mengambil ringkasan value object Progress dan Streak tanpa memuat detail atribut lain dari Habit.",
)
def get_habit_progress(habitId: UUID, current_user: User = Depends(get_current_user)) -> ProgressResponse:
    """
    Get progress and streak summary for a habit.
    
    - **habitId**: UUID of the habit to get progress for
    
    Requires: Valid JWT token in Authorization header
    """
    habit = habit_repository.get_by_id(habitId)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habit with id {habitId} not found",
        )
    
    # Ensure user can only access their own habits
    if habit.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this habit",
        )
    
    return habit_to_progress_response(habit)


# Register routers
router.include_router(auth_router)
router.include_router(habits_router)
