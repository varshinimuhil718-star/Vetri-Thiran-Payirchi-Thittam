from ..config import get_settings
from ..schemas import UserInput, WorkoutPlan
from .gemini_client import generate_structured


def update_workout_plan(*, user: UserInput, original_plan: WorkoutPlan, feedback: str) -> WorkoutPlan:
    settings = get_settings()

    if settings.mock_ai:
        updated = original_plan.model_copy(deep=True)
        updated.overview = (
            f"Updated after feedback: {feedback.strip()}. "
            "The sample plan remains conservative for UI testing."
        )
        return updated

    prompt = f"""
You are FitBuddy updating an existing 7-day wellness workout plan.

User:
Name: {user.username}
Age: {user.age}
Weight: {user.weight} kg
Goal: {user.goal}
Intensity: {user.intensity}

Original plan:
{original_plan.model_dump_json(indent=2)}

User feedback:
{feedback}

Create a revised plan with exactly 7 days.

Requirements:
- Preserve the user's goal unless feedback clearly requests a change.
- Apply the feedback where it is reasonable and safe.
- Do not encourage training through pain or concerning symptoms.
- Do not give medical diagnosis or treatment.
- Avoid extreme exercise, dehydration, starvation, or unsafe challenges.
- Keep progression gradual and include recovery.
"""

    raw = generate_structured(
        model=settings.workout_model,
        prompt=prompt,
        response_schema=WorkoutPlan,
    )
    return WorkoutPlan.model_validate_json(raw)
