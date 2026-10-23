
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AuthSession
from app.login_rate_limit import (
    client_key,
    check_login_limit,
    record_failed_login,
    clear_failed_logins,
)


router = APIRouter(prefix="/auth", tags=["Authentication"])
password_hasher = PasswordHasher()

COOKIE_NAME = "moneymate_session"
SESSION_DAYS = 7


def token_hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def utc_now():
    return datetime.now(timezone.utc)


def require_session(
    request: Request,
    db: Session = Depends(get_db),
) -> AuthSession:
    token = request.cookies.get(COOKIE_NAME)

    if not token:
        raise HTTPException(401, "Authentication required")

    session = db.scalar(
        select(AuthSession).where(
            AuthSession.token_hash == token_hash(token)
        )
    )

    if not session:
        raise HTTPException(401, "Invalid session")

    expires_at = session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at <= utc_now():
        raise HTTPException(401, "Session expired")

    if request.method not in ("GET", "HEAD", "OPTIONS"):
        csrf = request.headers.get("X-CSRF-Token", "")

        if not hmac.compare_digest(
            token_hash(csrf),
            session.csrf_token_hash,
        ):
            raise HTTPException(403, "Invalid CSRF token")

    return session


class LoginRequest(BaseModel):
    password: str



@router.post("/login")
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    key = client_key(request)

    check_login_limit(db, key)

    configured_hash = os.environ["MONEYMATE_PASSWORD_HASH"]

    try:
        valid = password_hasher.verify(
            configured_hash,
            payload.password,
        )
    except (VerifyMismatchError, VerificationError):
        valid = False

    if not valid:
        record_failed_login(db, key)
        raise HTTPException(
            status_code=401,
            detail="Invalid password",
        )

    session_token = secrets.token_urlsafe(32)
    csrf_token = secrets.token_urlsafe(32)

    db.add(
        AuthSession(
            token_hash=token_hash(session_token),
            csrf_token_hash=token_hash(csrf_token),
            expires_at=utc_now() + timedelta(days=SESSION_DAYS),
        )
    )

    db.commit()

    clear_failed_logins(db, key)

    secure = os.getenv("COOKIE_SECURE", "false").lower() == "true"

    response.set_cookie(
        key=COOKIE_NAME,
        value=session_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=SESSION_DAYS * 86400,
        path="/",
    )

    return {
        "authenticated": True,
        "csrf_token": csrf_token,
    }



@router.get("/me")
def me(
    request: Request,
    db: Session = Depends(get_db),
):
    session = require_session(request, db)

    # A fresh CSRF token is issued after page reload.
    csrf_token = secrets.token_urlsafe(32)
    session.csrf_token_hash = token_hash(csrf_token)
    db.commit()

    return {"authenticated": True, "csrf_token": csrf_token}


@router.post("/logout")
def logout(
    response: Response,
    session: AuthSession = Depends(require_session),
    db: Session = Depends(get_db),
):
    db.delete(session)
    db.commit()

    response.delete_cookie(COOKIE_NAME, path="/")
    return {"authenticated": False}
