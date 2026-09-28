import json

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..ai.nutrition_generator import generate_nutrition_tip_with_flash
from ..ai.plan_updater import update_workout_plan
from ..ai.workout_generator import generate_workout_gemini
from ..database import get_db
from ..models import User
from ..schemas import NutritionTip, UserInput, WorkoutPlan

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def render_error(request: Request, message: str, status_code: int = 400):
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={"message": message},
        status_code=status_code,
    )


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        user_input = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

        existing = db.scalar(select(User).where(User.user_id == user_input.user_id))
        if existing:
            return render_error(
                request,
                f"User ID '{user_input.user_id}' already exists. Use another ID.",
                409,
            )

        workout_plan = generate_workout_gemini(user_input)
        nutrition_tip = generate_nutrition_tip_with_flash(user_input)

        user = User(
            user_id=user_input.user_id,
            username=user_input.username,
            age=user_input.age,
            weight=user_input.weight,
            goal=user_input.goal,
            intensity=user_input.intensity,
            original_plan=workout_plan.model_dump_json(),
            nutrition_tip=nutrition_tip.model_dump_json(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "workout_plan": workout_plan,
                "nutrition_tip": nutrition_tip,
                "updated": False,
            },
        )
    except Exception as exc:
        db.rollback()
        return render_error(request, str(exc), 500)


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        user = db.scalar(select(User).where(User.user_id == user_id.strip()))
        if not user:
            return render_error(request, "User ID was not found.", 404)

        feedback = feedback.strip()
        if len(feedback) < 3:
            return render_error(request, "Please provide a little more feedback.", 400)

        user_input = UserInput(
            username=user.username,
            user_id=user.user_id,
            age=user.age,
            weight=user.weight,
            goal=user.goal,
            intensity=user.intensity,
        )

        original_model = WorkoutPlan.model_validate(json.loads(user.original_plan))
        updated_model = update_workout_plan(
            user=user_input,
            original_plan=original_model,
            feedback=feedback,
        )

        user.updated_plan = updated_model.model_dump_json()
        user.feedback = feedback
        db.commit()
        db.refresh(user)

        nutrition_tip = NutritionTip.model_validate_json(user.nutrition_tip)

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "workout_plan": updated_model,
                "nutrition_tip": nutrition_tip,
                "updated": True,
            },
        )
    except Exception as exc:
        db.rollback()
        return render_error(request, str(exc), 500)


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={"users": users},
    )


@router.post("/delete-user/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.user_id == user_id))
    if user:
        db.delete(user)
        db.commit()
    return RedirectResponse(url="/view-all-users", status_code=303)
