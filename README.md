# FitBuddy – AI Fitness Plan Generator

FitBuddy is a FastAPI + Jinja2 + SQLite web application based on the supplied FitBuddy specification. It accepts a user's name, ID, age, weight, goal, and workout intensity, generates a structured 7-day workout plan and a nutrition/recovery tip with Gemini, stores the results, and lets the user submit feedback to regenerate the plan.

## Modernized Gemini integration

The supplied document describes Gemini 1.5 Pro/Gemini Flash and the older `google-generativeai` SDK. Current Google documentation uses the `google-genai` Python SDK and current Gemini model names. This implementation therefore uses `google-genai` with configurable model names. The default is `gemini-3.8-flash`; change the model variables in `.env` if needed.

## Features

- Personalized 7-day workout plan
- Structured AI JSON output validated with Pydantic
- Nutrition/recovery tip
- Feedback-based plan regeneration
- SQLite persistence with SQLAlchemy
- Dashboard at `/view-all-users`
- REST API plus Jinja2 HTML interface
- Mock AI mode for testing without an API key
- Responsive frontend
- Basic validation and error handling

## Structure

```text
FitBuddy-AI/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── gemini_client.py
│   │   ├── workout_generator.py
│   │   ├── nutrition_generator.py
│   │   └── plan_updater.py
│   └── routes/
│       ├── __init__.py
│       ├── web.py
│       └── api.py
├── static/
│   ├── css/style.css
│   └── js/app.js
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── result.html
│   ├── all_users.html
│   └── error.html
├── tests/test_app.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Windows / VS Code

Open the project folder in VS Code and PowerShell in that folder.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Put your Gemini API key in `.env`.

For testing the entire application without Gemini, set:

```text
MOCK_AI=true
```

Then start:

```powershell
uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/view-all-users

## Automated tests

```powershell
pytest -q
```

The tests use mock AI mode and do not call Gemini.

## API

- `GET /api/health`
- `POST /api/generate-workout`
- `POST /api/submit-feedback`
- `GET /api/users`
- `GET /api/users/{user_id}`

## Safety

FitBuddy is a wellness-planning demonstration, not a medical diagnostic or treatment system. Its prompts avoid diagnosis, extreme dieting, dehydration, and unsafe exercise. Users should stop an activity that causes pain or other concerning symptoms and seek appropriate qualified help.
