import os
os.environ["MOCK_AI"] = "true"

from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "FitBuddy" in response.text


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_generate_and_feedback():
    payload = {
        "username": "Test User",
        "user_id": "TEST001",
        "age": 18,
        "weight": 70,
        "goal": "general wellness",
        "intensity": "low",
    }

    response = client.post("/api/generate-workout", json=payload)
    assert response.status_code == 200
    assert len(response.json()["workout_plan"]["days"]) == 7

    feedback = {
        "user_id": "TEST001",
        "feedback": "Make the sixth day lighter.",
    }
    response = client.post("/api/submit-feedback", json=feedback)
    assert response.status_code == 200
    assert len(response.json()["workout_plan"]["days"]) == 7


def test_users_list():
    response = client.get("/api/users")
    assert response.status_code == 200
    assert any(row["user_id"] == "TEST001" for row in response.json())


def test_user_page():
    response = client.get("/view-all-users")
    assert response.status_code == 200
    assert "Test User" in response.text
