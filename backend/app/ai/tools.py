
import json
from typing import Literal

from langchain_core.tools import tool

from app.database import SessionLocal
from app.summary_routes import account_balances, category_summary


@tool
def get_account_balances() -> str:
    """Get current balances for all accounts, including transfers."""
    with SessionLocal() as db:
        result = account_balances(db=db)

    return json.dumps(result, default=str)


@tool
def get_monthly_expenses() -> str:
    """Get total expenses for the current calendar month."""
    with SessionLocal() as db:
        result = category_summary(period="month", db=db)

    total = sum(
        (item["total"] for item in result["categories"]),
        start=0,
    )

    return json.dumps({
        "period": "month",
        "currency": "INR",
        "total_expenses": total,
    }, default=str)


@tool
def get_category_spending(
    period: Literal["day", "week", "month"] = "month",
) -> str:
    """Get expense totals grouped by category for today, this week, or this month."""
    with SessionLocal() as db:
        result = category_summary(period=period, db=db)

    return json.dumps(result, default=str)