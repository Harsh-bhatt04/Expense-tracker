
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Literal

from fastapi import HTTPException
from pydantic import ValidationError
from mcp.server.fastmcp import FastMCP

from app.database import SessionLocal
from app.summary_routes import account_balances, category_summary
from app.transaction_routes import TransactionCreate, create_transaction


mcp = FastMCP("MoneyMate Financial Tools")


# -------------------------------
# READ-ONLY TOOLS
# -------------------------------

@mcp.tool()
def get_account_balances() -> dict:
    """Get current balances of all bank accounts."""

    with SessionLocal() as db:
        result = account_balances(db=db)

    return {
        "accounts": [
            {
                **account,
                "opening_balance": str(account["opening_balance"]),
                "total_income": str(account["total_income"]),
                "total_expenses": str(account["total_expenses"]),
                "total_transfer_in": str(account["total_transfer_in"]),
                "total_transfer_out": str(account["total_transfer_out"]),
                "current_balance": str(account["current_balance"]),
            }
            for account in result["accounts"]
        ],
        "total_balance": str(result["total_balance"]),
    }


@mcp.tool()
def get_monthly_expenses() -> dict:
    """Get total expenses for the current month."""

    with SessionLocal() as db:
        result = category_summary(period="month", db=db)

    total = sum(
        (item["total"] for item in result["categories"]),
        Decimal("0"),
    )

    return {
        "period": "month",
        "currency": "INR",
        "total_expenses": str(total),
    }


@mcp.tool()
def get_category_spending(
    period: Literal["day", "week", "month"] = "month",
) -> dict:
    """Get category-wise spending for today, this week, or this month."""

    with SessionLocal() as db:
        result = category_summary(period=period, db=db)

    return {
        "period": period,
        "currency": "INR",
        "categories": [
            {
                "category": item["category"],
                "total": str(item["total"]),
            }
            for item in result["categories"]
        ],
    }


# -------------------------------
# WRITE TOOLS
# -------------------------------

@mcp.tool()
def add_transaction(
    account_id: int,
    transaction_type: Literal["expense", "income"],
    amount: str,
    category: str = "Other",
    description: str = "",
    transaction_date: str | None = None,
) -> dict:
    """
    Create an expense or income transaction.

    Requires user approval in LangGraph before execution.
    Amount must be positive.
    Date format: YYYY-MM-DD.
    """

    try:
        data = TransactionCreate(
            account_id=account_id,
            transaction_type=transaction_type,
            amount=Decimal(amount),
            category=category or "Other",
            description=description or None,
            transaction_date=(
                date.fromisoformat(transaction_date)
                if transaction_date
                else date.today()
            ),
        )

        with SessionLocal() as db:
            transaction = create_transaction(
                data=data,
                db=db,
            )

            return {
                "success": True,
                "transaction": {
                    "id": transaction.id,
                    "account_id": transaction.account_id,
                    "transaction_type": transaction.transaction_type,
                    "amount": str(transaction.amount),
                    "category": transaction.category,
                    "description": transaction.description,
                    "transaction_date": transaction.transaction_date.isoformat(),
                },
            }

    except (ValidationError, ValueError, InvalidOperation) as exc:
        return {
            "success": False,
            "error": str(exc),
        }

    except HTTPException as exc:
        return {
            "success": False,
            "error": str(exc.detail),
        }


# -------------------------------
# START MCP SERVER
# -------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")