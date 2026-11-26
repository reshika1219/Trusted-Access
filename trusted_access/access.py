from __future__ import annotations

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
            connection.execute(
                "UPDATE emergency_requests SET status = 'owner_approved' WHERE id = ?",
                (request_id,),
            )
            record_audit(connection, owner_id, "access_owner_approved", request_id, owner_id)
            connection.commit()
            return {"request_id": request_id, "status": "awaiting_contact_approvals"}

        grant_id, expires_at = _grant_access(
            connection,
            request_id,
            request["vault_item_id"],
            request["requester_contact_id"],
            owner_id,
        )
        connection.commit()
        return {"grant_id": grant_id, "expires_at": expires_at.isoformat()}

    @app.post("/access-requests/{request_id}/contact-approve", tags=["access"])
    def contact_approve_access_request(
        request_id: str,
        auth: tuple[str, Connection] = Depends(contact_context),
    ) -> dict[str, str]:
        contact_id, connection = auth
        request = connection.execute(
            """
            SELECT r.id, r.vault_item_id, r.requester_contact_id, r.status, v.owner_id,
                   p.required_approvals
            FROM emergency_requests r
            JOIN vault_items v ON v.id = r.vault_item_id
            JOIN access_policies p ON p.vault_item_id = v.id
            WHERE r.id = ?
            """,
            (request_id,),
        ).fetchone()
        if request is None:
            raise HTTPException(status_code=404, detail="Access request not found")
        if request["status"] not in {"pending", "owner_approved"}:
            raise HTTPException(status_code=409, detail="Access request is not awaiting approval")
        allowed = connection.execute(
            """
            SELECT 1 FROM policy_contacts pc
            JOIN access_policies p ON p.id = pc.policy_id
            WHERE p.vault_item_id = ? AND pc.contact_id = ?
            """,
            (request["vault_item_id"], contact_id),
        ).fetchone()
        if allowed is None:
            raise HTTPException(status_code=403, detail="Contact is not an approver for this item")
        try:
            connection.execute(
                """
                INSERT INTO approvals (id, request_id, contact_id, decision, decided_at)
                VALUES (?, ?, ?, 'approved', ?)
                """,
                (str(uuid4()), request_id, contact_id, utc_now().isoformat()),
            )
        except Exception as error:
            connection.rollback()
            if "UNIQUE constraint failed" in str(error):
                raise HTTPException(status_code=409, detail="Contact already approved this request") from error
            raise
        approvals = connection.execute(
            """
            SELECT COUNT(*) AS count FROM approvals
            WHERE request_id = ? AND decision = 'approved'
            """,
            (request_id,),
        ).fetchone()["count"]
        record_audit(connection, request["owner_id"], "access_approved", request_id, contact_id)
        if approvals < request["required_approvals"]:
            connection.commit()
            return {"request_id": request_id, "status": "awaiting_more_approvals"}
        grant_id, expires_at = _grant_access(
            connection,
            request_id,
            request["vault_item_id"],
            request["requester_contact_id"],
            request["owner_id"],
        )
        connection.commit()
        return {"grant_id": grant_id, "expires_at": expires_at.isoformat()}

    @app.post("/access-requests/{request_id}/reject", tags=["access"])
    def reject_access_request(
        request_id: str,
        auth: tuple[str, Connection] = Depends(owner_context),
    ) -> dict[str, str]:
        owner_id, connection = auth
        updated = connection.execute(
            """
            UPDATE emergency_requests SET status = 'rejected'
            WHERE id = ? AND status IN ('pending', 'owner_approved')
              AND vault_item_id IN (SELECT id FROM vault_items WHERE owner_id = ?)
            """,
            (request_id, owner_id),
        )
        if updated.rowcount != 1:
            raise HTTPException(status_code=404, detail="Pending access request not found")
        record_audit(connection, owner_id, "access_rejected", request_id, owner_id)
        connection.commit()
        return {"request_id": request_id, "status": "rejected"}

    @app.get("/access-grants", tags=["access"])
    def list_access_grants(
        auth: tuple[str, Connection] = Depends(owner_context),
    ) -> list[dict[str, Optional[str]]]:
        owner_id, connection = auth
        rows = connection.execute(
            """
            SELECT g.id, g.request_id, g.vault_item_id, g.recipient_contact_id,
                   g.expires_at, g.revoked_at, g.created_at
            FROM access_grants g
            JOIN vault_items v ON v.id = g.vault_item_id
            WHERE v.owner_id = ?
            ORDER BY g.created_at DESC
            """,
            (owner_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    @app.post("/access-grants/{grant_id}/revoke", tags=["access"])
    def revoke_grant(
        grant_id: str,
        auth: tuple[str, Connection] = Depends(owner_context),
    ) -> dict[str, str]:
        owner_id, connection = auth
        updated = connection.execute(
            """
            UPDATE access_grants SET revoked_at = ?
            WHERE id = ? AND revoked_at IS NULL
              AND vault_item_id IN (SELECT id FROM vault_items WHERE owner_id = ?)
            """,
            (utc_now().isoformat(), grant_id, owner_id),
        )
        if updated.rowcount != 1:
            raise HTTPException(status_code=404, detail="Active access grant not found")
        record_audit(connection, owner_id, "access_revoked", grant_id, owner_id)
        connection.commit()
        return {"grant_id": grant_id, "status": "revoked"}

    @app.get("/audit-events", tags=["audit"])
    def list_audit_events(
        auth: tuple[str, Connection] = Depends(owner_context),
    ) -> list[dict[str, str]]:
        owner_id, connection = auth
        rows = connection.execute(
            """
            SELECT id, event_type, actor_id, resource_id, metadata_json, created_at
            FROM audit_events WHERE owner_id = ? ORDER BY created_at DESC
            """,
            (owner_id,),
        ).fetchall()
        return [dict(row) for row in rows]

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


def _grant_access(
    connection: Connection,
    request_id: str,
    item_id: str,
    recipient_contact_id: str,
    owner_id: str,
) -> tuple[str, datetime]:
    existing = connection.execute(
        "SELECT id, expires_at FROM access_grants WHERE request_id = ? AND revoked_at IS NULL",
        (request_id,),
    ).fetchone()
    if existing is not None:
        return existing["id"], datetime.fromisoformat(existing["expires_at"])
    now = utc_now()
    expires_at = now + timedelta(hours=1)
    grant_id = str(uuid4())
    connection.execute(
        "UPDATE emergency_requests SET status = 'approved' WHERE id = ?",
        (request_id,),
    )
    connection.execute(
        """
        INSERT INTO access_grants
            (id, request_id, vault_item_id, recipient_contact_id, expires_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (grant_id, request_id, item_id, recipient_contact_id, expires_at.isoformat(), now.isoformat()),
    )
    record_audit(connection, owner_id, "access_granted", grant_id, owner_id)
    return grant_id, expires_at
