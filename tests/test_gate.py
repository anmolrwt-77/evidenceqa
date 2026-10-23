from src.config import REFUSE_MESSAGE
from src.generate import answer_question


def test_score_gate_refuses_when_no_chunks(monkeypatch):
    def fake_retrieve(question, k=3, min_score=0.5):
        return []

    monkeypatch.setattr("src.generate.retrieve", fake_retrieve)

    called = {"llm": False}

    def fake_generate_answer(question, chunks):
        called["llm"] = True
        return "should not happen"

    monkeypatch.setattr("src.generate.generate_answer", fake_generate_answer)

    result = answer_question("What is the best pizza topping in Tokyo?")

    assert result["refused"] is True
    assert result["answer"] == REFUSE_MESSAGE
    assert result["citations"] == []
    assert result["scores"] == []
    assert called["llm"] is False