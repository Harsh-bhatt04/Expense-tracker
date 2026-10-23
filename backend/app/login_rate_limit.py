
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models import LoginAttempt

MAX_FAILURES = 5
WINDOW = timedelta(minutes=15)


def client_key(request: Request) -> str:
    # Use the direct client address. Do not trust an
    # arbitrary X-Forwarded-For header.
    ip = request.client.host if request.client else "unknown"

    secret = os.environ["LOGIN_RATE_LIMIT_SECRET"]

    return hmac.new(
        secret.encode(),
        ip.encode(),
        hashlib.sha256,
    ).hexdigest()


def check_login_limit(db: Session, key: str) -> None:
    now = datetime.now(timezone.utc)

    attempt = db.scalar(
        select(LoginAttempt).where(
            LoginAttempt.ip_hash == key
        )
    )

    if attempt is None:
        return

    started = attempt.window_started_at

    if started.tzinfo is None:
        started = started.replace(tzinfo=timezone.utc)

    if now - started >= WINDOW:
        return

    if attempt.failed_count >= MAX_FAILURES:
        retry_after = max(
            1,
            int((started + WINDOW - now).total_seconds()) + 1,
        )

        raise HTTPException(
            status_code=429,
            detail="Too many failed login attempts. Try again later.",
            headers={"Retry-After": str(retry_after)},
        )


def record_failed_login(db: Session, key: str) -> None:
    now = datetime.now(timezone.utc)
    cutoff = now - WINDOW

    statement = insert(LoginAttempt).values(
        ip_hash=key,
        failed_count=1,
        window_started_at=now,
    )

    statement = statement.on_conflict_do_update(
        index_elements=[LoginAttempt.ip_hash],
        set_={
            "failed_count": (
                1
                if False
                else LoginAttempt.failed_count + 1
            ),
            "window_started_at": LoginAttempt.window_started_at,
        },
        where=LoginAttempt.window_started_at > cutoff,
    )

    # Expired windows must reset instead of retaining old counts.
    # The final upsert below handles both cases atomically.
    statement = insert(LoginAttempt).values(
        ip_hash=key,
        failed_count=1,
        window_started_at=now,
    )

    from sqlalchemy import case

    statement = statement.on_conflict_do_update(
        index_elements=[LoginAttempt.ip_hash],
        set_={
            "failed_count": case(
                (
                    LoginAttempt.window_started_at <= cutoff,
                    1,
                ),
                else_=LoginAttempt.failed_count + 1,
            ),
            "window_started_at": case(
                (
                    LoginAttempt.window_started_at <= cutoff,
                    now,
                ),
                else_=LoginAttempt.window_started_at,
            ),
        },
    )

    db.execute(statement)
    db.commit()


def clear_failed_logins(db: Session, key: str) -> None:
    db.execute(
        delete(LoginAttempt).where(
            LoginAttempt.ip_hash == key
        )
    )
    db.commit()
