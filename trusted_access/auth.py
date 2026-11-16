from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from sqlite3 import Connection
from typing import Optional
from uuid import uuid4

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from fastapi import HTTPException, status


SESSION_TTL = timedelta(hours=8)
PASSWORD_HASHER = PasswordHasher()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def timestamp(value: datetime) -> str:
    return value.isoformat()


def hash_password(password: str) -> str:
    return PASSWORD_HASHER.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        return PASSWORD_HASHER.verify(stored_hash, password)
    except (InvalidHashError, VerificationError, VerifyMismatchError):
        return False


def create_session(connection: Connection, user_id: str) -> str:
    raw_token = secrets.token_urlsafe(32)
    expires_at = utc_now() + SESSION_TTL
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    connection.execute(
        """
        INSERT INTO sessions (token_hash, user_id, created_at, expires_at)
        VALUES (?, ?, ?, ?)
        """,
        (token_hash, user_id, timestamp(utc_now()), timestamp(expires_at)),
    )
    connection.commit()
    return raw_token


def user_from_session(connection: Connection, token: Optional[str]) -> str:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    row = connection.execute(
        "SELECT user_id, expires_at FROM sessions WHERE token_hash = ?",
        (token_hash,),
    ).fetchone()
    if row is None or datetime.fromisoformat(row["expires_at"]) <= utc_now():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")
    return row["user_id"]
def new_user_id() -> str:
    return str(uuid4())
