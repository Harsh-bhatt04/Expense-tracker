
from uuid import UUID
from typing import Literal, Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    conversation_id: UUID
    message: str = Field(min_length=1)


class ApprovalRequest(BaseModel):
    conversation_id: UUID
    approved: bool


class ChatResponse(BaseModel):
    conversation_id: UUID
    status: Literal["completed", "approval_required"]
    response: str
    approval: dict[str, Any] | None = None