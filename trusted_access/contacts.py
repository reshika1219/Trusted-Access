from __future__ import annotations

from sqlite3 import Connection
from typing import Optional
from uuid import uuid4

from fastapi import Depends, HTTPException, Header, status
from pydantic import BaseModel, Field

from trusted_access.auth import user_from_session, utc_now
from trusted_access.main import database
from trusted_access.vault import record_audit


class ContactCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    relationship: str = Field(min_length=1, max_length=100)
    contact_method: str = Field(min_length=1, max_length=320)


class PolicyCreate(BaseModel):
    access_mode: str = Field(pattern="^(specific_contacts|emergency_only|time_limited)$")
    contact_ids: list[str] = Field(min_length=1, max_length=20)
    required_approvals: int = Field(default=1, ge=1, le=20)


def context(
    x_session_token: Optional[str] = Header(default=None),
    connection: Connection = Depends(database),
) -> tuple[str, Connection]:
    return user_from_session(connection, x_session_token), connection


def register_routes(app) -> None:
    @app.post("/trusted-contacts", status_code=status.HTTP_201_CREATED, tags=["contacts"])
    def create_contact(
        request: ContactCreate,
        auth: tuple[str, Connection] = Depends(context),
    ) -> dict[str, str]:
        owner_id, connection = auth
        contact_id = str(uuid4())
        connection.execute(
            """
            INSERT INTO trusted_contacts
                (id, owner_id, name, relationship, contact_method, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                contact_id,
                owner_id,
                request.name,
                request.relationship,
                request.contact_method,
                utc_now().isoformat(),
            ),
        )
        record_audit(connection, owner_id, "trusted_contact_created", contact_id, owner_id)
        connection.commit()
        return {"contact_id": contact_id}

    @app.get("/trusted-contacts", tags=["contacts"])
    def list_contacts(
        auth: tuple[str, Connection] = Depends(context),
    ) -> list[dict[str, str]]:
        owner_id, connection = auth
        rows = connection.execute(
            """
            SELECT id, name, relationship, contact_method, created_at
            FROM trusted_contacts
            WHERE owner_id = ?
            ORDER BY created_at
            """,
            (owner_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    @app.put("/vault/items/{item_id}/policy", tags=["permissions"])
    def set_policy(
        item_id: str,
        request: PolicyCreate,
        auth: tuple[str, Connection] = Depends(context),
    ) -> dict[str, str]:
        owner_id, connection = auth
        item = connection.execute(
            "SELECT id FROM vault_items WHERE id = ? AND owner_id = ?",
            (item_id, owner_id),
        ).fetchone()
        if item is None:
            raise HTTPException(status_code=404, detail="Vault item not found")
        if request.required_approvals > len(request.contact_ids):
            raise HTTPException(
                status_code=422,
                detail="Required approvals cannot exceed selected contacts",
            )
        placeholders = ",".join("?" for _ in request.contact_ids)
        contacts = connection.execute(
            f"""
            SELECT id FROM trusted_contacts
            WHERE owner_id = ? AND id IN ({placeholders})
            """,
            [owner_id, *request.contact_ids],
        ).fetchall()
        if len(contacts) != len(set(request.contact_ids)):
            raise HTTPException(status_code=422, detail="Contact is not owned by this user")

        policy_id = str(uuid4())
        connection.execute(
            """
            INSERT INTO access_policies
                (id, vault_item_id, access_mode, required_approvals, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                policy_id,
                item_id,
                request.access_mode,
                request.required_approvals,
                utc_now().isoformat(),
            ),
        )
        connection.executemany(
            "INSERT INTO policy_contacts (policy_id, contact_id) VALUES (?, ?)",
            [(policy_id, contact_id) for contact_id in set(request.contact_ids)],
        )
        record_audit(connection, owner_id, "access_policy_changed", item_id, owner_id)
        connection.commit()
        return {"policy_id": policy_id}
