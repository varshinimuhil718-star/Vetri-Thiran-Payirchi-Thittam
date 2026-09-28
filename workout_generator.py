from ..config import get_settings
from ..schemas import UserInput, WorkoutPlan
from .gemini_client import generate_structured


def mock_workout_plan(user: UserInput) -> WorkoutPlan:
    focuses = [
        "Full body mobility",
        "Lower body",
        "Upper body",
        "Light cardio",
        "Core and stability",
        "Full body strength",
        "Recovery and flexibility",
    ]

    days = []
    for index, focus in enumerate(focuses, start=1):
        if index in {4, 7}:
            exercises = [
                {
                    "name": "Brisk walk",
                    "duration_minutes": 20,
                    "notes": "Keep the pace comfortable and controlled.",
                },
                {
                    "name": "Gentle mobility",
                    "duration_minutes": 10,
                    "notes": "Move through a comfortable range of motion.",
                },
            ]
        else:
            exercises = [
                {"name": "Bodyweight squat", "sets": 2, "reps": "8-12", "rest_seconds": 60},
                {"name": "Wall push-up", "sets": 2, "reps": "8-12", "rest_seconds": 60},
                {"name": "Glute bridge", "sets": 2, "reps": "10-12", "rest_seconds": 60},
            ]

        days.append({
            "day": f"Day {index}",
            "focus": focus,
            "warmup": "5 minutes of easy walking and gentle mobility.",
            "exercises": exercises,
            "cooldown": "5 minutes of easy movement and comfortable stretching.",
            "recovery_note": "Rest or reduce intensity if you feel pain, dizziness, or unusual discomfort.",
        })

    return WorkoutPlan(
        title=f"7-Day FitBuddy Plan for {user.goal.title()}",
        overview=(
            f"A beginner-friendly plan for {user.username}, using {user.intensity} "
            "intensity and gradual progression."
        ),
        days=days,
    )


def generate_workout_gemini(user: UserInput) -> WorkoutPlan:
    settings = get_settings()

    if settings.mock_ai:
        return mock_workout_plan(user)

    prompt = f"""
You are FitBuddy, a conservative wellness and fitness planning assistant.

Create a structured 7-day workout plan for:
Name: {user.username}
Age: {user.age}
Weight: {user.weight} kg
Goal: {user.goal}
Preferred intensity: {user.intensity}

Requirements:
- Return exactly 7 days.
- Include warm-up, main exercises, cooldown, and a recovery note each day.
- Use exercise names, sets/reps or duration, rest where appropriate, and short notes.
- Match the requested intensity without encouraging dangerous overexertion.
- Include rest/recovery where appropriate.
- Avoid diagnosing conditions or giving medical treatment.
- Do not recommend extreme dieting, dehydration, starvation, or unsafe exercise challenges.
- If future feedback mentions pain, illness, dizziness, chest symptoms, or other concerning symptoms,
  prioritize stopping the activity and seeking qualified medical advice.
- This is general wellness guidance, not a medical prescription.
"""

    raw = generate_structured(
        model=settings.workout_model,
        prompt=prompt,
        response_schema=WorkoutPlan,
    )
    return WorkoutPlan.model_validate_json(raw)
