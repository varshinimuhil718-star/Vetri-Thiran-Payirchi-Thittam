from ..config import get_settings
from ..schemas import NutritionTip, UserInput
from .gemini_client import generate_structured


def mock_nutrition_tip(user: UserInput) -> NutritionTip:
    return NutritionTip(
        tip="Build regular meals around a protein source, vegetables or other nutrient-rich foods, and enough fluids.",
        why_it_matters="Balanced meals can support recovery, energy, and consistency with training.",
        simple_action="At your next meal, include a protein-rich food and drink water according to your thirst.",
    )


def generate_nutrition_tip_with_flash(user: UserInput) -> NutritionTip:
    settings = get_settings()

    if settings.mock_ai:
        return mock_nutrition_tip(user)

    prompt = f"""
You are FitBuddy's nutrition and recovery assistant.

Give one concise, practical nutrition or recovery tip for:
Age: {user.age}
Weight: {user.weight} kg
Goal: {user.goal}
Workout intensity: {user.intensity}

Rules:
- Keep it general and wellness-oriented.
- Do not prescribe a restrictive calorie target.
- Do not recommend fasting, purging, dehydration, supplements, or extreme diets.
- Avoid diagnosing deficiencies or medical conditions.
- Emphasize sustainable eating, hydration, sleep, and recovery as appropriate.
"""

    raw = generate_structured(
        model=settings.tip_model,
        prompt=prompt,
        response_schema=NutritionTip,
        temperature=0.3,
    )
    return NutritionTip.model_validate_json(raw)
