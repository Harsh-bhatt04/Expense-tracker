
from fastapi import APIRouter, HTTPException

from app.ai.agent import run_agent
from app.ai.schemas import ChatRequest, ChatResponse


router = APIRouter(prefix="/chat", tags=["AI Chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        answer = await run_agent(request.message)

        return ChatResponse(response=answer)

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="AI service is temporarily unavailable.",
        )