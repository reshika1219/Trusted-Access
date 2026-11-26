from pathlib import Path
import hashlib
import os
import time
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

from trusted_access.auth import (
    create_session,
    hash_password,
    new_user_id,
    user_from_session,
    verify_password,
)
from trusted_access.database import connect

app = FastAPI(
    title="Trusted Access",
    description=(
        "Privacy-first prototype for controlled emergency information sharing. "
        "This service is not production-secure or legally certified."
    ),
    version="0.1.0",
)
app.state.database_path = Path(
    os.environ.get("TRUSTED_ACCESS_DB", ".data/trusted_access.sqlite3")
)


def database():
    app.state.database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = connect(app.state.database_path)
    try:
        yield connection
    finally:
        connection.close()


# Failed-login throttling is per process and per email address. It slows online
# password guessing; it is not a substitute for a shared rate limiter in a real
# deployment, and it lets someone lock out a known email for the window.
LOGIN_WINDOW_SECONDS = 15 * 60
LOGIN_MAX_FAILURES = 10
LOGIN_TRACKED_LIMIT = 10_000
_login_failures: dict[str, list[float]] = {}


def _recent_failures(email: str) -> list[float]:
    cutoff = time.monotonic() - LOGIN_WINDOW_SECONDS
    recent = [moment for moment in _login_failures.get(email, []) if moment > cutoff]
    if recent:
        _login_failures[email] = recent
    else:
        _login_failures.pop(email, None)
    return recent


def reset_login_throttle() -> None:
    _login_failures.clear()


class RegisterRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=12, max_length=256)


class LoginRequest(RegisterRequest):
    pass


def normalized_email(email: str) -> str:
    return email.strip().lower()


@app.post("/auth/register", status_code=status.HTTP_201_CREATED, tags=["authentication"])
def register(request: RegisterRequest, connection=Depends(database)) -> dict[str, str]:
    email = normalized_email(request.email)
    user_id = new_user_id()
    try:
        connection.execute(
            """
            INSERT INTO users (id, email, password_hash, created_at)
            VALUES (?, ?, ?, datetime('now'))
            """,
            (user_id, email, hash_password(request.password)),
        )
        connection.commit()
    except Exception as error:
        connection.rollback()
        if "UNIQUE constraint failed: users.email" in str(error):
            raise HTTPException(status_code=409, detail="An account already exists for that email") from error
        raise
    token = create_session(connection, user_id)
    return {"user_id": user_id, "session_token": token}


@app.post("/auth/login", tags=["authentication"])
def login(request: LoginRequest, connection=Depends(database)) -> dict[str, str]:
    email = normalized_email(request.email)
    if len(_recent_failures(email)) >= LOGIN_MAX_FAILURES:
        raise HTTPException(
            status_code=429,
            detail="Too many failed sign-in attempts. Please wait a few minutes and try again.",
        )
    row = connection.execute(
        "SELECT id, password_hash FROM users WHERE email = ?",
        (email,),
    ).fetchone()
    if row is None or not verify_password(request.password, row["password_hash"]):
        if len(_login_failures) < LOGIN_TRACKED_LIMIT or email in _login_failures:
            _login_failures.setdefault(email, []).append(time.monotonic())
        raise HTTPException(status_code=401, detail="Invalid email or password")
    _login_failures.pop(email, None)
    return {"session_token": create_session(connection, row["id"])}


@app.post("/auth/logout", tags=["authentication"])
def logout(
    x_session_token: Optional[str] = Header(default=None),
    connection=Depends(database),
) -> dict[str, str]:
    if x_session_token:
        connection.execute(
            "DELETE FROM sessions WHERE token_hash = ?",
            (hashlib.sha256(x_session_token.encode("utf-8")).hexdigest(),),
        )
        connection.commit()
    return {"status": "signed_out"}


@app.get("/auth/me", tags=["authentication"])
def current_user(
    x_session_token: Optional[str] = Header(default=None),
    connection=Depends(database),
) -> dict[str, str]:
    user_id = user_from_session(connection, x_session_token)
    row = connection.execute("SELECT id, email FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=401, detail="Invalid session")
    return {"user_id": row["id"], "email": row["email"]}


from trusted_access.vault import register_routes as register_vault_routes

register_vault_routes(app)

from trusted_access.contacts import register_routes as register_contact_routes

register_contact_routes(app)

from trusted_access.requests import register_routes as register_request_routes

register_request_routes(app)

from trusted_access.access import register_routes as register_access_routes

register_access_routes(app)

from trusted_access.backup import register_routes as register_backup_routes

register_backup_routes(app)

from trusted_access.ui import register_ui

register_ui(app)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}
