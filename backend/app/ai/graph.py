
import json

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import interrupt

from langchain_core.messages import (
    AIMessage,
    SystemMessage,
    ToolMessage,
)

from app.ai.prompts import SYSTEM_PROMPT


WRITE_TOOLS = {"add_transaction"}


class MoneyMateState(MessagesState):
    approved: bool | None


def build_graph(model, checkpointer, tools):
    model_with_tools = model.bind_tools(
        tools,
    )

    tool_node = ToolNode(tools)

    async def chatbot(state: MoneyMateState):
        response = await model_with_tools.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            *state["messages"],
        ])

        return {
            "messages": [response],
            "approved": None,
        }

    def approval(state: MoneyMateState):
        calls = state["messages"][-1].tool_calls

        writes = [
            call for call in calls
            if call["name"] in WRITE_TOOLS
        ]

        if not writes:
            return {"approved": True}

        # Never approve multiple writes or mixed tool batches.
        if len(calls) != 1 or len(writes) != 1:
            return {"approved": False}

        decision = interrupt({
            "message": "Approve this transaction?",
            "actions": [
                {
                    "tool": writes[0]["name"],
                    "arguments": writes[0]["args"],
                }
            ],
        })

        return {"approved": decision is True}

    def approval_route(state: MoneyMateState):
        return "tools" if state["approved"] else "rejected"

    def rejected(state: MoneyMateState):
        calls = state["messages"][-1].tool_calls

        return {
            "messages": [
                ToolMessage(
                    content="Transaction cancelled. No changes were made.",
                    tool_call_id=call["id"],
                )
                for call in calls
            ]
        }

    def after_rejection(state: MoneyMateState):
        return {
            "messages": [
                AIMessage(
                    content="Transaction cancelled. No changes were made."
                )
            ]
        }

    def after_tools(state: MoneyMateState):
        last_tool = state["messages"][-1]

        # Find the tool call that produced this result.
        last_call = next(
            (
                msg
                for msg in reversed(state["messages"])
                if isinstance(msg, AIMessage) and msg.tool_calls
            ),
            None,
        )

        if not last_call:
            return "chatbot"

        if (
            len(last_call.tool_calls) == 1
            and last_call.tool_calls[0]["name"] == "add_transaction"
        ):
            return "transaction_result"

        return "chatbot"

    def transaction_result(state: MoneyMateState):
        tool_message = state["messages"][-1]
        content = tool_message.content

        try:
            if isinstance(content, str):
                result = json.loads(content)
            elif isinstance(content, dict):
                result = content
            elif isinstance(content, list):
                text = next(
                    (
                        item.get("text")
                        for item in content
                        if isinstance(item, dict) and item.get("text")
                    ),
                    None,
                )
                result = json.loads(text) if text else {}
            else:
                result = {}

            # Handle MCP responses wrapped in a result object
            if isinstance(result, dict) and "result" in result:
                result = result["result"]

            if isinstance(result, str):
                result = json.loads(result)

        except (ValueError, TypeError, AttributeError):
            result = {}

        if result.get("success"):
            transaction = result["transaction"]

            response = (
                "Transaction saved successfully.\n\n"
                f"Amount: ₹{transaction['amount']}\n"
                f"Type: {transaction['transaction_type'].title()}\n"
                f"Category: {transaction['category']}\n"
                f"Transaction ID: {transaction['id']}"
            )
        elif result.get("success") is False:
            response = (
                "Transaction could not be saved: "
                f"{result.get('error', 'Unknown error')}"
            )
        else:
            response = (
                "Unable to verify the transaction result. "
                "Please check your transaction history before retrying."
            )

        return {"messages": [AIMessage(content=response)]}

    builder = StateGraph(MoneyMateState)

    builder.add_node("chatbot", chatbot)
    builder.add_node("approval", approval)
    builder.add_node("tools", tool_node)
    builder.add_node("rejected", rejected)
    builder.add_node("after_rejection", after_rejection)
    builder.add_node("transaction_result", transaction_result)

    builder.add_edge(START, "chatbot")

    builder.add_conditional_edges(
        "chatbot",
        tools_condition,
        {
            "tools": "approval",
            "__end__": END,
        },
    )

    builder.add_conditional_edges(
        "approval",
        approval_route,
        {
            "tools": "tools",
            "rejected": "rejected",
        },
    )

    builder.add_conditional_edges(
        "tools",
        after_tools,
        {
            "transaction_result": "transaction_result",
            "chatbot": "chatbot",
        },
    )

    builder.add_edge("transaction_result", END)

    builder.add_edge("rejected", "after_rejection")
    builder.add_edge("after_rejection", END)

    return builder.compile(checkpointer=checkpointer)