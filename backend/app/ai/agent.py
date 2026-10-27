
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.types import Command

from app.ai.graph import build_graph


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


@asynccontextmanager
async def agent_lifespan():
    checkpoint_url = os.environ["CHECKPOINT_DATABASE_URL"]

    client = MultiServerMCPClient(
    {
        "money": {
            "transport": "stdio",
            "command": sys.executable,
            "args": ["-m", "app.mcp_server.server"],
            "cwd": str(BASE_DIR),
            "env": {
                **os.environ,
                "DATABASE_URL": os.environ["DATABASE_URL"],
            },
        }
    }
)

    async with AsyncPostgresSaver.from_conn_string(
        checkpoint_url
    ) as checkpointer:

        await checkpointer.setup()

        tools = await client.get_tools()
        print("Loaded MCP tools:", [tool.name for tool in tools])

        model = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash-lite"
        )

        graph = build_graph(
            model=model,
            checkpointer=checkpointer,
            tools=tools,
        )

        yield graph


def format_result(result: dict) -> dict:
    interrupts = result.get("__interrupt__", [])

    if interrupts:
        return {
            "status": "approval_required",
            "response": "Please review the transaction details below.",
            "approval": interrupts[0].value,
        }

    messages = result.get("messages", [])

    if not messages:
        return {
            "status": "completed",
            "response": "No response was generated.",
            "approval": None,
        }

    content = messages[-1].content

    if isinstance(content, str):
        response = content
    else:
        response = " ".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict)
            and block.get("type") == "text"
        )

    return {
        "status": "completed",
        "response": response,
        "approval": None,
    }


async def run_agent(graph, message: str, thread_id: str) -> dict:
    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    result = await graph.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": message,
                }
            ]
        },
        config=config,
    )

    return format_result(result)


async def resume_agent(
    graph,
    thread_id: str,
    approved: bool,
) -> dict:
    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    result = await graph.ainvoke(
        Command(resume=approved),
        config=config,
    )

    return format_result(result)
