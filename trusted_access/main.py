from pathlib import Path
import os
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
    row = connection.execute(
        "SELECT id, password_hash FROM users WHERE email = ?",
        (normalized_email(request.email),),
    ).fetchone()
    if row is None or not verify_password(request.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"session_token": create_session(connection, row["id"])}


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


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}
