from fastapi.testclient import TestClient

from src.api import app
from src.config import MIN_SCORE


client = TestClient(app)


def test_health_ok():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "evidenceqa"
    assert data["min_score"] == MIN_SCORE


def test_ask_rejects_empty_question():
    response = client.post("/ask", json={"question": "   "})
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()