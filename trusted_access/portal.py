from __future__ import annotations

from sqlite3 import Connection

from fastapi import Depends

from trusted_access.auth import utc_now
from trusted_access.main import database
from trusted_access.requests import contact_context


def register_routes(app) -> None:
    """Read-only views for a signed-in trusted contact.

    These endpoints never return ciphertext; contacts only see item metadata for
    items an owner explicitly shared with them through an access policy.
    """

    @app.get("/contact/me", tags=["contact portal"])
    def contact_profile(
        auth: tuple[str, Connection] = Depends(contact_context),
    ) -> dict[str, str]:
        contact_id, connection = auth
        row = connection.execute(
            "SELECT id, name, relationship FROM trusted_contacts WHERE id = ?",
            (contact_id,),
        ).fetchone()
        return dict(row)

    @app.get("/contact/items", tags=["contact portal"])
    def contact_items(
        auth: tuple[str, Connection] = Depends(contact_context),
    ) -> list[dict[str, object]]:
        contact_id, connection = auth
        rows = connection.execute(
            """
            SELECT v.id, v.title, v.category, p.access_mode, p.required_approvals
            FROM vault_items v
            JOIN access_policies p ON p.vault_item_id = v.id
            JOIN policy_contacts pc ON pc.policy_id = p.id
            WHERE pc.contact_id = ?
            ORDER BY v.title
            """,
            (contact_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    @app.get("/contact/requests", tags=["contact portal"])
    def contact_requests(
        auth: tuple[str, Connection] = Depends(contact_context),
    ) -> dict[str, list[dict[str, object]]]:
        contact_id, connection = auth
        now = utc_now().isoformat()
        mine = [
            dict(row)
            for row in connection.execute(
                """
                SELECT r.id, r.vault_item_id, v.title AS item_title, r.status, r.requested_at,
                       p.required_approvals,
                       (SELECT COUNT(*) FROM approvals a
                        WHERE a.request_id = r.id AND a.decision = 'approved') AS approvals,
                       g.id AS grant_id, g.expires_at AS grant_expires_at,
                       g.revoked_at AS grant_revoked_at
                FROM emergency_requests r
                JOIN vault_items v ON v.id = r.vault_item_id
                JOIN access_policies p ON p.vault_item_id = v.id
                LEFT JOIN access_grants g ON g.request_id = r.id
                WHERE r.requester_contact_id = ?
                ORDER BY r.requested_at DESC
                """,
                (contact_id,),
            ).fetchall()
        ]
        to_approve = [
            dict(row)
            for row in connection.execute(
                """
                SELECT r.id, r.vault_item_id, v.title AS item_title, r.status, r.requested_at,
                       c.name AS requester_name, p.required_approvals,
                       (SELECT COUNT(*) FROM approvals a
                        WHERE a.request_id = r.id AND a.decision = 'approved') AS approvals
                FROM emergency_requests r
                JOIN vault_items v ON v.id = r.vault_item_id
                JOIN access_policies p ON p.vault_item_id = v.id
                JOIN policy_contacts pc ON pc.policy_id = p.id AND pc.contact_id = ?
                JOIN trusted_contacts c ON c.id = r.requester_contact_id
                WHERE r.status IN ('pending', 'owner_approved')
                  AND r.requester_contact_id != ?
                  AND NOT EXISTS (
                      SELECT 1 FROM approvals a
                      WHERE a.request_id = r.id AND a.contact_id = ?
                  )
                ORDER BY r.requested_at DESC
                """,
                (contact_id, contact_id, contact_id),
            ).fetchall()
        ]
        for request in mine:
            expired = request["grant_expires_at"] is not None and request["grant_expires_at"] <= now
            request["grant_active"] = bool(
                request["grant_id"] and not request["grant_revoked_at"] and not expired
            )
        return {"mine": mine, "to_approve": to_approve}
