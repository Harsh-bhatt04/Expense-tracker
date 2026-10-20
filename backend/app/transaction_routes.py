
from datetime import date
from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import Account, Transaction

router = APIRouter(prefix="/transactions", tags=["Transactions"])


class TransactionCreate(BaseModel):
    account_id: int
    transaction_type: Literal["expense", "income"]
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    category: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    transaction_date: date = Field(default_factory=date.today)


class TransactionResponse(BaseModel):
    id: int
    account_id: int
    transaction_type: str
    amount: Decimal
    category: str | None
    description: str | None
    transaction_date: date

    model_config = {"from_attributes": True}

def verify_existing(existing: Transaction, data: TransactionCreate,) -> Transaction:
    if (
        existing.account_id != data.account_id
        or existing.transaction_type != data.transaction_type
        or existing.amount != data.amount
        or existing.category != data.category
        or existing.description != data.description
        or existing.transaction_date != data.transaction_date
    ):
        raise HTTPException(
            status_code=409,
            detail="Idempotency key belongs to another transaction.",
        )

    return existing

@router.post("/", response_model=TransactionResponse, status_code=201)
def create_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    *,
    idempotency_key: str | None = None,
):
    if idempotency_key:
        existing = db.scalar(
            select(Transaction).where(
                Transaction.idempotency_key == idempotency_key
            )
        )

        if existing is not None:
            return verify_existing(existing, data)

    account = db.get(Account, data.account_id)

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found",
        )

    transaction = Transaction(
        account_id=data.account_id,
        transaction_type=data.transaction_type,
        amount=data.amount,
        category=data.category,
        description=data.description,
        transaction_date=data.transaction_date,
        idempotency_key=idempotency_key,
    )

    try:
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    except IntegrityError:
        db.rollback()

        if idempotency_key:
            existing = db.scalar(
                select(Transaction).where(
                    Transaction.idempotency_key == idempotency_key
                )
            )

            if existing is not None:
                return verify_existing(existing, data)

        raise


@router.get("/", response_model=list[TransactionResponse])
def list_transactions(
    account_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(Transaction)

    if account_id is not None:
        query = query.filter(Transaction.account_id == account_id)

    if start_date is not None:
        query = query.filter(Transaction.transaction_date >= start_date)

    if end_date is not None:
        query = query.filter(Transaction.transaction_date <= end_date)

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date must not be after end_date",
        )

    return query.order_by(
        Transaction.transaction_date.desc(),
        Transaction.id.desc(),
    ).limit(limit).all()


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    data: TransactionCreate,
    db: Session = Depends(get_db),
):
    transaction = db.get(Transaction, transaction_id)

    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if db.get(Account, data.account_id) is None:
        raise HTTPException(status_code=404, detail="Account not found")

    transaction.account_id = data.account_id
    transaction.transaction_type = data.transaction_type
    transaction.amount = data.amount
    transaction.category = data.category
    transaction.description = data.description
    transaction.transaction_date = data.transaction_date

    db.commit()
    db.refresh(transaction)
    return transaction


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
):
    transaction = db.get(Transaction, transaction_id)

    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(transaction)
    db.commit()
    return Response(status_code=204)
