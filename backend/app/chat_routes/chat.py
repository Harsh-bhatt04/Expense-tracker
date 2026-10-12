
from fastapi import APIRouter, HTTPException, Request
from langgraph.types import Command

from app.ai.agent import run_agent, resume_agent
from app.ai.schemas import (
    ChatRequest,
    ChatResponse,
    ApprovalRequest,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["AI Chat"])


@router.post("/", response_model=ChatResponse)
async def chat(payload: ChatRequest, request: Request):
    graph = request.app.state.graph
    config = {
        "configurable": {
            "thread_id": str(payload.conversation_id)
        }
    }

    try:
        snapshot = await graph.aget_state(config)

        if any(task.interrupts for task in snapshot.tasks):
            raise HTTPException(
                status_code=409,
                detail="Resolve the pending action first.",
            )

        result = await run_agent(
            graph,
            payload.message,
            str(payload.conversation_id),
        )

        return ChatResponse(
            conversation_id=payload.conversation_id,
            **result,
        )

    except HTTPException:
        raise
    except Exception:
        logger.exception("Chat agent execution failed")
    raise HTTPException(
        status_code=503,
        detail="AI service is temporarily unavailable.",
    )


@router.post("/resume", response_model=ChatResponse)
async def resume(payload: ApprovalRequest, request: Request):
    graph = request.app.state.graph
    config = {
        "configurable": {
            "thread_id": str(payload.conversation_id)
        }
    }

    try:
        snapshot = await graph.aget_state(config)

        has_interrupt = any(
            task.interrupts
            for task in snapshot.tasks
        )

        if not has_interrupt:
            raise HTTPException(
                status_code=409,
                detail="No pending approval found.",
            )

        result = await resume_agent(
            graph,
            str(payload.conversation_id),
            payload.approved,
        )

        return ChatResponse(
            conversation_id=payload.conversation_id,
            **result,
        )

    except HTTPException:
        raise
    except Exception:
        logger.exception("Chat agent execution failed")
    raise HTTPException(
        status_code=503,
        detail="AI service is temporarily unavailable.",
    )