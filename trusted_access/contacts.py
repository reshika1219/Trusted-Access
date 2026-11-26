from __future__ import annotations

import hashlib
import secrets
from sqlite3 import Connection
from datetime import timedelta
from typing import Optional
from uuid import uuid4

from fastapi import Depends, HTTPException, Header, status
from pydantic import BaseModel, Field

from trusted_access.auth import user_from_session, utc_now
from trusted_access.main import database
from trusted_access.vault import clear_item_shares, record_audit


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


def _enforce_policy(
    connection: Connection, owner_id: str, item_id: str, allowed_contact_ids: set[str]
) -> None:
    """End access for anyone the current policy no longer includes.

    Open requests from contacts outside the policy are rejected and their active
    grants are revoked, so narrowing or removing sharing takes effect at once.
    """
    allowed = list(allowed_contact_ids)
    # With no allowed contacts every open request and grant is stale. (A bare
    # "NOT IN (NULL)" would match nothing in SQL, so omit the clause instead.)
    marks = ",".join("?" for _ in allowed)
    request_filter = f"AND requester_contact_id NOT IN ({marks})" if allowed else ""
    grant_filter = f"AND recipient_contact_id NOT IN ({marks})" if allowed else ""
    stale_requests = connection.execute(
        f"""
        SELECT id FROM emergency_requests
        WHERE vault_item_id = ? AND status IN ('pending', 'owner_approved')
          {request_filter}
        """,
        [item_id, *allowed],
    ).fetchall()
    for row in stale_requests:
        connection.execute(
            "UPDATE emergency_requests SET status = 'rejected' WHERE id = ?", (row["id"],)
        )
        record_audit(connection, owner_id, "access_rejected", row["id"], owner_id)
    stale_grants = connection.execute(
        f"""
        SELECT id FROM access_grants
        WHERE vault_item_id = ? AND revoked_at IS NULL
          {grant_filter}
        """,
        [item_id, *allowed],
    ).fetchall()
    for row in stale_grants:
        connection.execute(
            "UPDATE access_grants SET revoked_at = ? WHERE id = ?",
            (utc_now().isoformat(), row["id"]),
        )
        record_audit(connection, owner_id, "access_revoked", row["id"], owner_id)


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

    @app.post("/trusted-contacts/{contact_id}/invite", tags=["contacts"])
    def create_contact_invite(
        contact_id: str,
        auth: tuple[str, Connection] = Depends(context),
    ) -> dict[str, str]:
        owner_id, connection = auth
        contact = connection.execute(
            "SELECT id FROM trusted_contacts WHERE id = ? AND owner_id = ?",
            (contact_id, owner_id),
        ).fetchone()
        if contact is None:
            raise HTTPException(status_code=404, detail="Trusted contact not found")
        raw_token = secrets.token_urlsafe(32)
        connection.execute(
            """
            INSERT INTO contact_sessions (token_hash, contact_id, created_at, expires_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                hashlib.sha256(raw_token.encode("utf-8")).hexdigest(),
                contact_id,
                utc_now().isoformat(),
                (utc_now() + timedelta(days=7)).isoformat(),
            ),
        )
        record_audit(connection, owner_id, "trusted_contact_invited", contact_id, owner_id)
        connection.commit()
        return {"contact_token": raw_token}

    @app.delete("/trusted-contacts/{contact_id}", tags=["contacts"])
    def delete_contact(
        contact_id: str,
        auth: tuple[str, Connection] = Depends(context),
    ) -> dict[str, str]:
        # Invites, requests, approvals, policy membership, and grants for the
        # contact are removed by foreign-key cascade.
        owner_id, connection = auth
        deleted = connection.execute(
            "DELETE FROM trusted_contacts WHERE id = ? AND owner_id = ?",
            (contact_id, owner_id),
        )
        if deleted.rowcount != 1:
            raise HTTPException(status_code=404, detail="Trusted contact not found")
        record_audit(connection, owner_id, "trusted_contact_deleted", contact_id, owner_id)
        connection.commit()
        return {"contact_id": contact_id, "status": "deleted"}

    @app.get("/trusted-contacts", tags=["contacts"])
    def list_contacts(
        auth: tuple[str, Connection] = Depends(context),
    ) -> list[dict[str, object]]:
        owner_id, connection = auth
        rows = connection.execute(
            """
            SELECT id, name, relationship, contact_method, created_at,
                   public_key, key_confirmed_at IS NOT NULL AS key_confirmed
            FROM trusted_contacts
            WHERE owner_id = ?
            ORDER BY created_at
            """,
            (owner_id,),
        ).fetchall()
        contacts = [dict(row) for row in rows]
        for contact in contacts:
            contact["key_confirmed"] = bool(contact["key_confirmed"])
        return contacts

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

        # Replace, never accumulate: stale policies would keep granting access.
        connection.execute("DELETE FROM access_policies WHERE vault_item_id = ?", (item_id,))
        clear_item_shares(connection, item_id)  # the owner re-publishes with fresh keys
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
        _enforce_policy(connection, owner_id, item_id, set(request.contact_ids))
        record_audit(connection, owner_id, "access_policy_changed", item_id, owner_id)
        connection.commit()
        return {"policy_id": policy_id}

    @app.get("/vault/items/{item_id}/policy", tags=["permissions"])
    def get_policy(
        item_id: str,
        auth: tuple[str, Connection] = Depends(context),
    ) -> dict[str, object]:
        owner_id, connection = auth
        item = connection.execute(
            "SELECT id FROM vault_items WHERE id = ? AND owner_id = ?",
            (item_id, owner_id),
        ).fetchone()
        if item is None:
            raise HTTPException(status_code=404, detail="Vault item not found")
        policy = connection.execute(
            """
            SELECT id, access_mode, required_approvals FROM access_policies
            WHERE vault_item_id = ? ORDER BY created_at DESC LIMIT 1
            """,
            (item_id,),
        ).fetchone()
        if policy is None:
            return {"policy": None}
        contact_ids = [
            row["contact_id"]
            for row in connection.execute(
                "SELECT contact_id FROM policy_contacts WHERE policy_id = ? ORDER BY contact_id",
                (policy["id"],),
            ).fetchall()
        ]
        return {
            "policy": {
                "access_mode": policy["access_mode"],
                "required_approvals": policy["required_approvals"],
                "contact_ids": contact_ids,
            }
        }

    @app.delete("/vault/items/{item_id}/policy", tags=["permissions"])
    def delete_policy(
        item_id: str,
        auth: tuple[str, Connection] = Depends(context),
    ) -> dict[str, str]:
        """Stop sharing an item: removes its rules, open requests, and active grants."""
        owner_id, connection = auth
        item = connection.execute(
            "SELECT id FROM vault_items WHERE id = ? AND owner_id = ?",
            (item_id, owner_id),
        ).fetchone()
        if item is None:
            raise HTTPException(status_code=404, detail="Vault item not found")
        connection.execute("DELETE FROM access_policies WHERE vault_item_id = ?", (item_id,))
        clear_item_shares(connection, item_id)
        _enforce_policy(connection, owner_id, item_id, set())
        record_audit(connection, owner_id, "access_policy_removed", item_id, owner_id)
        connection.commit()
        return {"item_id": item_id, "status": "not_shared"}
