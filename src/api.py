import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.config import MIN_SCORE
from src.generate import answer_question


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="EvidenceQA",
    description="Grounded AI policy question answering with retrieval score gate.",
    version="0.1.0",
)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)


class Citation(BaseModel):
    source: str
    index: int
    score: float


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    scores: list[float]
    refused: bool


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "evidenceqa", "min_score": MIN_SCORE}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="question must not be empty")

    logger.info("api /ask question=%r", question)
    result = answer_question(question)

    return AskResponse(
        answer=result["answer"],
        citations=result["citations"],
        scores=result["scores"],
        refused=result["refused"],
    )