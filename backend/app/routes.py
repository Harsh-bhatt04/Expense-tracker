
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Account

router = APIRouter(prefix="/accounts", tags=["Accounts"])


class AccountCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    opening_balance: Decimal = Field(default=Decimal("0.00"), ge=0)


class AccountResponse(BaseModel):
    id: int
    name: str
    opening_balance: Decimal
    currency: str

    model_config = {"from_attributes": True}


@router.post("/", response_model=AccountResponse, status_code=201)
def create_account(
    account_data: AccountCreate,
    db: Session = Depends(get_db),
):
    name = account_data.name.strip()

    if not name:
        raise HTTPException(status_code=422, detail="Account name cannot be empty")

    existing = db.query(Account).filter(Account.name == name).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail="An account with this name already exists",
        )

    account = Account(
        name=name,
        opening_balance=account_data.opening_balance,
        currency="INR",
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return account


@router.get("/", response_model=list[AccountResponse])
def list_accounts(db: Session = Depends(get_db)):
    return db.query(Account).order_by(Account.id).all()

