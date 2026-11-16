from __future__ import annotations

import json
from sqlite3 import Connection
from typing import Optional
from uuid import uuid4

from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel, Field

from trusted_access.auth import user_from_session, utc_now
from trusted_access.main import database


ALLOWED_CATEGORIES = {
    "Medical",
    "Emergency contacts",
    "Insurance",
    "Documents",
    "Property",
    "Dependents",
    "Pets",
    "Instructions",
}


class VaultItemCreate(BaseModel):
    category: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=200)
    ciphertext: str = Field(min_length=1, max_length=2_000_000)


def current_user_and_database(
    x_session_token: Optional[str] = Header(default=None),
    connection: Connection = Depends(database),
) -> tuple[str, Connection]:
    return user_from_session(connection, x_session_token), connection


def record_audit(
    connection: Connection,
    owner_id: str,
    event_type: str,
    resource_id: str,
    actor_id: Optional[str] = None,
) -> None:
    connection.execute(
        """
        INSERT INTO audit_events
            (id, owner_id, event_type, actor_id, resource_id, metadata_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(uuid4()),
            owner_id,
            event_type,
            actor_id,
            resource_id,
            json.dumps({}),
            utc_now().isoformat(),
        ),
    )


def register_routes(app) -> None:
    @app.post("/vault/items", status_code=status.HTTP_201_CREATED, tags=["vault"])
    def create_vault_item(
        request: VaultItemCreate,
        context: tuple[str, Connection] = Depends(current_user_and_database),
    ) -> dict[str, str]:
        owner_id, connection = context
        if request.category not in ALLOWED_CATEGORIES:
            raise HTTPException(status_code=422, detail="Unsupported vault category")
        item_id = str(uuid4())
        now = utc_now().isoformat()
        connection.execute(
            """
            INSERT INTO vault_items
                (id, owner_id, category, title, ciphertext, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item_id,
                owner_id,
                request.category,
                request.title,
                request.ciphertext,
                now,
                now,
            ),
        )
        record_audit(connection, owner_id, "vault_item_created", item_id, owner_id)
        connection.commit()
        return {"item_id": item_id}

    @app.get("/vault/items", tags=["vault"])
    def list_vault_items(
        context: tuple[str, Connection] = Depends(current_user_and_database),
    ) -> list[dict[str, str]]:
        owner_id, connection = context
        rows = connection.execute(
            """
            SELECT id, category, title, ciphertext, created_at, updated_at
            FROM vault_items
            WHERE owner_id = ?
            ORDER BY created_at
            """,
            (owner_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    @app.get("/vault/items/{item_id}", tags=["vault"])
    def get_vault_item(
        item_id: str,
        context: tuple[str, Connection] = Depends(current_user_and_database),
    ) -> dict[str, str]:
        owner_id, connection = context
        row = connection.execute(
            """
            SELECT id, category, title, ciphertext, created_at, updated_at
            FROM vault_items
            WHERE id = ? AND owner_id = ?
            """,
            (item_id, owner_id),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Vault item not found")
        return dict(row)
