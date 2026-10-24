import logging
import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.config import MIN_SCORE
from src.generate import answer_question
from src.store import index_is_ready


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
    ready = index_is_ready()
    return {
        "status": "ok" if ready else "degraded",
        "service": "evidenceqa",
        "min_score": MIN_SCORE,
        "index_ready": ready,
    }


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    request_id = str(uuid.uuid4())[:8]
    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="question must not be empty")

    if not index_is_ready():
        logger.error("request_id=%s index missing or empty", request_id)
        raise HTTPException(
            status_code=503,
            detail="Document index is not ready. Run: python scripts/build_index.py",
        )

    logger.info("request_id=%s /ask received", request_id)

    try:
        result = answer_question(question)
    except RuntimeError as exc:
        # Safe message to client; details already logged in generate.py
        logger.error("request_id=%s failed: %s", request_id, str(exc))
        raise HTTPException(
            status_code=503,
            detail="Answer service temporarily unavailable. Please try again later.",
        ) from exc
    except Exception:
        logger.exception("request_id=%s unexpected failure", request_id)
        raise HTTPException(
            status_code=500,
            detail="Internal server error.",
        )

    logger.info(
        "request_id=%s done refused=%s citation_count=%s",
        request_id,
        result["refused"],
        len(result["citations"]),
    )

    return AskResponse(
        answer=result["answer"],
        citations=result["citations"],
        scores=result["scores"],
        refused=result["refused"],
    )