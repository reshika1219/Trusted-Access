from __future__ import annotations

import hashlib
from datetime import datetime, timedelta
from sqlite3 import Connection
from typing import Optional
from uuid import uuid4

from fastapi import Depends, Header, HTTPException, status

from trusted_access.auth import user_from_session, utc_now
from trusted_access.main import database
from trusted_access.requests import contact_context
from trusted_access.vault import record_audit


def owner_context(
    x_session_token: Optional[str] = Header(default=None),
    connection: Connection = Depends(database),
) -> tuple[str, Connection]:
    return user_from_session(connection, x_session_token), connection


def register_routes(app) -> None:
    @app.get("/access-requests", tags=["access"])
    def list_access_requests(
        auth: tuple[str, Connection] = Depends(owner_context),
    ) -> list[dict[str, str]]:
        owner_id, connection = auth
        rows = connection.execute(
            """
            SELECT r.id, r.vault_item_id, r.requester_contact_id, r.status, r.requested_at
            FROM emergency_requests r
            JOIN vault_items v ON v.id = r.vault_item_id
            WHERE v.owner_id = ?
            ORDER BY r.requested_at DESC
            """,
            (owner_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    @app.post("/access-requests/{request_id}/approve", tags=["access"])
    def approve_access_request(
        request_id: str,
        auth: tuple[str, Connection] = Depends(owner_context),
    ) -> dict[str, str]:
        owner_id, connection = auth
        request = connection.execute(
            """
            SELECT r.id, r.vault_item_id, r.requester_contact_id, r.status
            FROM emergency_requests r
            JOIN vault_items v ON v.id = r.vault_item_id
            WHERE r.id = ? AND v.owner_id = ?
            """,
            (request_id, owner_id),
        ).fetchone()
        if request is None:
            raise HTTPException(status_code=404, detail="Access request not found")
        if request["status"] != "pending":
            raise HTTPException(status_code=409, detail="Access request is not pending")

        policy = connection.execute(
            """
            SELECT required_approvals
            FROM access_policies
            WHERE vault_item_id = ?
            """,
            (request["vault_item_id"],),
        ).fetchone()
        if policy is None:
            raise HTTPException(status_code=403, detail="No access policy exists for this item")
        if policy["required_approvals"] != 1:
            raise HTTPException(
                status_code=409,
                detail="This item requires multi-party approval, which is not enabled yet",
            )

        now = utc_now()
        expires_at = now + timedelta(hours=1)
        grant_id = str(uuid4())
        connection.execute(
            "UPDATE emergency_requests SET status = 'approved' WHERE id = ?",
            (request_id,),
        )
        connection.execute(
            """
            INSERT INTO approvals (id, request_id, contact_id, decision, decided_at)
            VALUES (?, ?, ?, 'approved', ?)
            """,
            (str(uuid4()), request_id, request["requester_contact_id"], now.isoformat()),
        )
        connection.execute(
            """
            INSERT INTO access_grants
                (id, request_id, vault_item_id, recipient_contact_id, expires_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                grant_id,
                request_id,
                request["vault_item_id"],
                request["requester_contact_id"],
                expires_at.isoformat(),
                now.isoformat(),
            ),
        )
        record_audit(connection, owner_id, "access_granted", grant_id, owner_id)
        connection.commit()
        return {"grant_id": grant_id, "expires_at": expires_at.isoformat()}

    @app.get("/access-grants/{grant_id}", tags=["access"])
    def view_grant(
        grant_id: str,
        auth: tuple[str, Connection] = Depends(contact_context),
    ) -> dict[str, str]:
        contact_id, connection = auth
        row = connection.execute(
            """
            SELECT g.id, g.expires_at, g.revoked_at, v.id AS item_id,
                   v.category, v.title, v.ciphertext
            FROM access_grants g
            JOIN vault_items v ON v.id = g.vault_item_id
            WHERE g.id = ? AND g.recipient_contact_id = ?
            """,
            (grant_id, contact_id),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Access grant not found")
        if row["revoked_at"] is not None:
            raise HTTPException(status_code=403, detail="Access grant has been revoked")
        if datetime.fromisoformat(row["expires_at"]) <= utc_now():
            raise HTTPException(status_code=403, detail="Access grant has expired")
        owner_id = connection.execute(
            "SELECT owner_id FROM vault_items WHERE id = ?", (row["item_id"],)
        ).fetchone()["owner_id"]
        record_audit(connection, owner_id, "access_viewed", grant_id, contact_id)
        connection.commit()
        return {
            "item_id": row["item_id"],
            "category": row["category"],
            "title": row["title"],
            "ciphertext": row["ciphertext"],
            "expires_at": row["expires_at"],
        }
