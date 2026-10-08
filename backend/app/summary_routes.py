
from datetime import date, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Account, Transaction

router = APIRouter(prefix="/summary", tags=["Summary"])


@router.get("/balances")
def account_balances(db: Session = Depends(get_db)):
    accounts = db.query(Account).order_by(Account.id).all()
    results = []

    for account in accounts:
        transactions = db.query(
            Transaction.transaction_type,
            func.sum(Transaction.amount).label("total"),
        ).filter(
            Transaction.account_id == account.id
        ).group_by(
            Transaction.transaction_type
        ).all()

        totals = {
            transaction_type: Decimal(str(total or 0))
            for transaction_type, total in transactions
        }

        income = totals.get("income", Decimal("0.00"))
        expenses = totals.get("expense", Decimal("0.00"))
        transfer_in = totals.get("transfer_in", Decimal("0.00"))
        transfer_out = totals.get("transfer_out", Decimal("0.00"))

        balance = (
            account.opening_balance
            + income
            + transfer_in
            - expenses
            - transfer_out
        )

        results.append({
            "account_id": account.id,
            "account_name": account.name,
            "opening_balance": account.opening_balance,
            "total_income": income,
            "total_expenses": expenses,
            "total_transfer_in": transfer_in,
            "total_transfer_out": transfer_out,
            "current_balance": balance,
            "currency": account.currency,
        })

    return {
        "accounts": results,
        "total_balance": sum(
            (item["current_balance"] for item in results),
            Decimal("0.00"),
        ),
    }


@router.get("/categories")
def category_summary(
    period: str = "month",
    db: Session = Depends(get_db),
):
    from datetime import timedelta
    from fastapi import HTTPException

    today = date.today()

    if period == "day":
        start_date = today
    elif period == "week":
        start_date = today - timedelta(days=today.weekday())
    elif period == "month":
        start_date = today.replace(day=1)
    else:
        raise HTTPException(
            status_code=422,
            detail="period must be 'day', 'week', or 'month'",
        )

    results = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label("total"),
    ).filter(
        Transaction.transaction_type == "expense",
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= today,
    ).group_by(
        Transaction.category
    ).order_by(
        func.sum(Transaction.amount).desc()
    ).all()

    return {
        "period": period,
        "categories": [
            {
                "category": category or "Others",
                "total": total,
            }
            for category, total in results
        ],
    }
