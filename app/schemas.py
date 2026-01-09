from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProgressSchema(BaseModel):
    """Value object representing habit progress"""

    completedEntries: int = Field(default=0, description="Number of completed habit entries")
    totalEntries: int = Field(default=0, description="Total number of habit entries")
    percentage: int = Field(default=0, description="Completion percentage")


class StreakSchema(BaseModel):
    """Value object representing habit streak"""

    count: int = Field(default=0, description="Current streak count")


# Request Schemas
class CreateHabitRequest(BaseModel):
    """Request body for creating a new habit"""

    title: str = Field(..., description="Title of the habit")
    description: str = Field(..., description="Description of the habit")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Morning Exercise",
                "description": "Do 30 minutes of exercise every morning",
            }
        }
    }


# Response Schemas
class HabitResponse(BaseModel):
    """Full habit response with all details"""

    habitId: UUID = Field(..., description="Unique habit identifier")
    userId: UUID = Field(..., description="User ID who owns the habit")
    title: str = Field(..., description="Title of the habit")
    description: str = Field(..., description="Description of the habit")
    progress: ProgressSchema = Field(..., description="Progress tracking")
    streak: StreakSchema = Field(..., description="Streak tracking")
    created_at: datetime = Field(..., description="Timestamp when habit was created")
    updated_at: datetime = Field(..., description="Timestamp when habit was last updated")

    model_config = {
        "json_schema_extra": {
            "example": {
                "habitId": "123e4567-e89b-12d3-a456-426614174000",
                "userId": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Morning Exercise",
                "description": "Do 30 minutes of exercise every morning",
                "progress": {"completedEntries": 15, "totalEntries": 20, "percentage": 75},
                "streak": {"count": 5},
                "created_at": "2026-01-09T08:00:00",
                "updated_at": "2026-01-09T10:30:00",
            }
        }
    }


class HabitCompletionResponse(BaseModel):
    """Response after completing or missing a habit"""

    habitId: UUID = Field(..., description="Unique habit identifier")
    progress: ProgressSchema = Field(..., description="Updated progress")
    streak: StreakSchema = Field(..., description="Updated streak")

    model_config = {
        "json_schema_extra": {
            "example": {
                "habitId": "123e4567-e89b-12d3-a456-426614174000",
                "progress": {"completedEntries": 16, "totalEntries": 21, "percentage": 76},
                "streak": {"count": 6},
            }
        }
    }


class ProgressResponse(BaseModel):
    """Response with only progress and streak information"""

    progress: ProgressSchema = Field(..., description="Progress tracking")
    streak: StreakSchema = Field(..., description="Streak tracking")

    model_config = {
        "json_schema_extra": {
            "example": {
                "progress": {"completedEntries": 15, "totalEntries": 20, "percentage": 75},
                "streak": {"count": 5},
            }
        }
    }


# Authentication Schemas
class LoginRequest(BaseModel):
    """Request body for user login"""

    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="Password for authentication")

    model_config = {
        "json_schema_extra": {"example": {"username": "john_doe", "password": "secure_password123"}}
    }


class TokenResponse(BaseModel):
    """Response containing JWT access token"""

    accessToken: str = Field(..., description="JWT access token")
    tokenType: str = Field(default="Bearer", description="Token type")

    model_config = {
        "json_schema_extra": {
            "example": {
                "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "tokenType": "Bearer",
            }
        }
    }
