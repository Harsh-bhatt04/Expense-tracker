
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    opening_balance: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        default="INR",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class Transaction(Base):
    __tablename__ = "transactions"

    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="ck_transaction_amount_positive",
        ),
        CheckConstraint(
            "transaction_type IN "
            "('expense', 'income', 'transfer_in', 'transfer_out')",
            name="ck_transaction_type_valid",
        ),
        Index(
            "ix_transactions_date_account",
            "transaction_date",
            "account_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=False,
    )
    transaction_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    transaction_date: Mapped[date] = mapped_column(
        Date,
        default=date.today,
        nullable=False,
    )
    # Shared identifier for the two sides of an account transfer.
    transfer_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )