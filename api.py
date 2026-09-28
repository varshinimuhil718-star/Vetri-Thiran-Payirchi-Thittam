from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..ai.nutrition_generator import generate_nutrition_tip_with_flash
from ..ai.plan_updater import update_workout_plan
from ..ai.workout_generator import generate_workout_gemini
from ..database import get_db
from ..models import User
from ..schemas import FeedbackRequest, NutritionTip, PlanResponse, UserInput, WorkoutPlan

router = APIRouter(prefix="/api", tags=["FitBuddy API"])


@router.get("/health")
def health():
    return {"status": "ok", "service": "FitBuddy"}


@router.post("/generate-workout", response_model=PlanResponse)
def api_generate_workout(payload: UserInput, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.user_id == payload.user_id)):
        raise HTTPException(status_code=409, detail="User ID already exists.")

    try:
        plan = generate_workout_gemini(payload)
        tip = generate_nutrition_tip_with_flash(payload)

        user = User(
            user_id=payload.user_id,
            username=payload.username,
            age=payload.age,
            weight=payload.weight,
            goal=payload.goal,
            intensity=payload.intensity,
            original_plan=plan.model_dump_json(),
            nutrition_tip=tip.model_dump_json(),
        )
        db.add(user)
        db.commit()

        return PlanResponse(
            user_id=payload.user_id,
            username=payload.username,
            goal=payload.goal,
            intensity=payload.intensity,
            workout_plan=plan,
            nutrition_tip=tip,
        )
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/submit-feedback", response_model=PlanResponse)
def api_submit_feedback(payload: FeedbackRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.user_id == payload.user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User ID not found.")

    try:
        user_input = UserInput(
            username=user.username,
            user_id=user.user_id,
            age=user.age,
            weight=user.weight,
            goal=user.goal,
            intensity=user.intensity,
        )
        original = WorkoutPlan.model_validate_json(user.original_plan)
        updated = update_workout_plan(
            user=user_input,
            original_plan=original,
            feedback=payload.feedback,
        )

        user.updated_plan = updated.model_dump_json()
        user.feedback = payload.feedback
        db.commit()

        tip = NutritionTip.model_validate_json(user.nutrition_tip)

        return PlanResponse(
            user_id=user.user_id,
            username=user.username,
            goal=user.goal,
            intensity=user.intensity,
            workout_plan=updated,
            nutrition_tip=tip,
        )
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/users")
def api_users(db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    return [
        {
            "user_id": user.user_id,
            "username": user.username,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
            "has_updated_plan": bool(user.updated_plan),
        }
        for user in users
    ]


@router.get("/users/{user_id}")
def api_get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.user_id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    return {
        "user_id": user.user_id,
        "username": user.username,
        "age": user.age,
        "weight": user.weight,
        "goal": user.goal,
        "intensity": user.intensity,
        "original_plan": WorkoutPlan.model_validate_json(user.original_plan),
        "updated_plan": WorkoutPlan.model_validate_json(user.updated_plan) if user.updated_plan else None,
        "nutrition_tip": NutritionTip.model_validate_json(user.nutrition_tip),
        "feedback": user.feedback,
    }
