from __future__ import annotations

import hashlib
from datetime import datetime
from sqlite3 import Connection
from typing import Optional
from uuid import uuid4

from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel

from trusted_access.auth import utc_now
from trusted_access.main import database
from trusted_access.vault import record_audit


class AccessRequestCreate(BaseModel):
    item_id: str


def contact_context(
    x_contact_token: Optional[str] = Header(default=None),
    connection: Connection = Depends(database),
) -> tuple[str, Connection]:
    if not x_contact_token:
        raise HTTPException(status_code=401, detail="Contact authentication required")
    row = connection.execute(
        """
        SELECT contact_id, expires_at
        FROM contact_sessions
        WHERE token_hash = ?
        """,
        (hashlib.sha256(x_contact_token.encode("utf-8")).hexdigest(),),
    ).fetchone()
    if row is None or datetime.fromisoformat(row["expires_at"]) <= utc_now():
        raise HTTPException(status_code=401, detail="Invalid or expired contact session")
    return row["contact_id"], connection


def register_routes(app) -> None:
    @app.post("/access-requests", status_code=status.HTTP_201_CREATED, tags=["access"])
    def create_access_request(
        request: AccessRequestCreate,
        auth: tuple[str, Connection] = Depends(contact_context),
    ) -> dict[str, str]:
        contact_id, connection = auth
        row = connection.execute(
            """
            SELECT v.id, v.owner_id, p.id AS policy_id
            FROM vault_items v
            JOIN access_policies p ON p.vault_item_id = v.id
            JOIN policy_contacts pc ON pc.policy_id = p.id
            WHERE v.id = ? AND pc.contact_id = ?
            """,
            (request.item_id, contact_id),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=403, detail="Contact is not permitted to request this item")
        request_id = str(uuid4())
        connection.execute(
            """
            INSERT INTO emergency_requests
                (id, vault_item_id, requester_contact_id, status, requested_at)
            VALUES (?, ?, ?, 'pending', ?)
            """,
            (request_id, request.item_id, contact_id, utc_now().isoformat()),
        )
        record_audit(
            connection,
            row["owner_id"],
            "access_requested",
            request_id,
            contact_id,
        )
        connection.commit()
        return {"request_id": request_id, "status": "pending"}
