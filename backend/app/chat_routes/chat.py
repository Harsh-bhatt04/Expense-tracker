
import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from langchain_core.messages import HumanMessage, AIMessage

from app.ai.agent import run_agent, resume_agent
from app.ai.schemas import (
    ChatRequest,
    ChatResponse,
    ApprovalRequest,
)


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["AI Chat"])


def extract_text(content):
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        return "\n".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict)
            and "text" in block
        )

    return ""


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
        logger.exception("Chat approval failed")
        raise HTTPException(
            status_code=503,
            detail="Unable to resume the conversation.",
        )


@router.get("/history/{conversation_id}")
async def get_chat_history(
    conversation_id: UUID,
    request: Request,
):
    graph = request.app.state.graph

    config = {
        "configurable": {
            "thread_id": str(conversation_id)
        }
    }

    snapshot = await graph.aget_state(config)

    if not snapshot.values:
        return {
            "messages": [],
            "pending_approval": None,
        }

    messages = []

    for message in snapshot.values.get("messages", []):

        # User messages
        if isinstance(message, HumanMessage):
            content = extract_text(message.content)

            if content.strip():
                messages.append({
                    "role": "user",
                    "content": content,
                })

        # Assistant messages
        elif isinstance(message, AIMessage):

            # Ignore internal MCP tool calls
            if message.tool_calls:
                continue

            content = extract_text(message.content)

            if content.strip():
                messages.append({
                    "role": "assistant",
                    "content": content,
                })

    # Restore pending approval
    pending_approval = None

    for task in snapshot.tasks:
        if task.interrupts:
            pending_approval = task.interrupts[0].value
            break

    return {
        "messages": messages,
        "pending_approval": pending_approval,
    }
