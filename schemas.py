from typing import Literal

from pydantic import BaseModel, Field, field_validator

Goal = Literal["weight loss", "muscle gain", "general wellness", "flexibility"]
Intensity = Literal["low", "medium", "high"]


class UserInput(BaseModel):
    username: str = Field(min_length=2, max_length=100)
    user_id: str = Field(min_length=2, max_length=80)
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=20, lt=400)
    goal: Goal
    intensity: Intensity

    @field_validator("username", "user_id")
    @classmethod
    def clean_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty.")
        return value


class Exercise(BaseModel):
    name: str
    sets: int | None = None
    reps: str | None = None
    duration_minutes: int | None = None
    rest_seconds: int | None = None
    notes: str | None = None


class WorkoutDay(BaseModel):
    day: str
    focus: str
    warmup: str
    exercises: list[Exercise]
    cooldown: str
    recovery_note: str


class WorkoutPlan(BaseModel):
    title: str
    overview: str
    days: list[WorkoutDay] = Field(min_length=7, max_length=7)


class NutritionTip(BaseModel):
    tip: str
    why_it_matters: str
    simple_action: str


class FeedbackRequest(BaseModel):
    user_id: str = Field(min_length=2, max_length=80)
    feedback: str = Field(min_length=3, max_length=1000)


class PlanResponse(BaseModel):
    user_id: str
    username: str
    goal: str
    intensity: str
    workout_plan: WorkoutPlan
    nutrition_tip: NutritionTip
