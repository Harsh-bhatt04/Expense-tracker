
from pathlib import Path
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

from app.ai.prompts import SYSTEM_PROMPT
from app.ai.tools import (
    get_account_balances,
    get_monthly_expenses,
    get_category_spending,
)

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3,
)

agent = create_agent(
    model=model,
    tools=[
        get_account_balances,
        get_monthly_expenses,
        get_category_spending,
    ],
    system_prompt=SYSTEM_PROMPT,
)


async def run_agent(message: str) -> str:
    result = await agent.ainvoke({
        "messages": [
            {"role": "user", "content": message}
        ]
    })

    content = result["messages"][-1].content

    if isinstance(content, str):
        return content

    return " ".join(
        block.get("text", "")
        for block in content
        if isinstance(block, dict)
        and block.get("type") == "text"
    )