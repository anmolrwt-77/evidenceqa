from fastapi.testclient import TestClient

from src.api import app
from src.config import MIN_SCORE


client = TestClient(app)


def test_health_ok():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in {"ok", "degraded"}
    assert data["service"] == "evidenceqa"
    assert data["min_score"] == MIN_SCORE
    assert "index_ready" in data


def test_ask_rejects_empty_question():
    response = client.post("/ask", json={"question": "   "})
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_ask_returns_503_when_llm_fails(monkeypatch):
    monkeypatch.setattr("src.api.index_is_ready", lambda: True)

    def boom(question):
        raise RuntimeError("LLM service unavailable")

    monkeypatch.setattr("src.api.answer_question", boom)

    response = client.post(
        "/ask",
        json={"question": "What are the four NIST AI RMF functions?"},
    )
    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"].lower()


def test_ask_returns_503_when_index_missing(monkeypatch):
    monkeypatch.setattr("src.api.index_is_ready", lambda: False)

    response = client.post(
        "/ask",
        json={"question": "What are the four NIST AI RMF functions?"},
    )
    assert response.status_code == 503
    assert "index" in response.json()["detail"].lower()