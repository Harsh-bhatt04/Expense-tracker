
from datetime import date
from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Account, Transaction

router = APIRouter(prefix="/transfers", tags=["Transfers"])


class TransferCreate(BaseModel):
    source_account_id: int
    destination_account_id: int
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    description: str | None = Field(default=None, max_length=500)
    transaction_date: date = Field(default_factory=date.today)


@router.post("/", status_code=201)
def create_transfer(
    data: TransferCreate,
    db: Session = Depends(get_db),
):
    if data.source_account_id == data.destination_account_id:
        raise HTTPException(
            status_code=422,
            detail="Source and destination accounts must be different",
        )

    source = db.get(Account, data.source_account_id)
    destination = db.get(Account, data.destination_account_id)

    if source is None or destination is None:
        raise HTTPException(status_code=404, detail="Account not found")

    transfer_id = str(uuid4())

    source_transaction = Transaction(
    account_id=source.id,
    transaction_type="transfer_out",
    amount=data.amount,
    description=data.description or f"Transfer to {destination.name}",
    transaction_date=data.transaction_date,
    transfer_id=transfer_id,
)

    destination_transaction = Transaction(
    account_id=destination.id,
    transaction_type="transfer_in",
    amount=data.amount,
    description=data.description or f"Transfer from {source.name}",
    transaction_date=data.transaction_date,
    transfer_id=transfer_id,
)

    try:
        db.add_all([source_transaction, destination_transaction])
        db.commit()
    except Exception:
        db.rollback()
        raise


    return {
        "message": "Transfer recorded successfully",
        "transfer_id": transfer_id,
        "source_account": source.name,
        "destination_account": destination.name,
        "amount": data.amount,
    }

