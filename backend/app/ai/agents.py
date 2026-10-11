
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.ai.prompts import SYSTEM_PROMPT


model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3,
)


async def run_agent(message: str) -> str:
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=message),
    ]

    result = await model.ainvoke(messages)

    if isinstance(result.content, str):
        return result.content

    return " ".join(
        block.get("text", "")
        for block in result.content
        if isinstance(block, dict) and block.get("type") == "text"
    )