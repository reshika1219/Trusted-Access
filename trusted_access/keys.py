from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
from sqlite3 import Connection
from typing import Optional

from fastapi import Depends, Header, HTTPException
from pydantic import BaseModel, Field

from trusted_access.auth import user_from_session, utc_now
from trusted_access.main import database
from trusted_access.requests import contact_context
from trusted_access.vault import clear_item_shares, record_audit

"""Key delivery for trusted contacts.

The server never sees a decryption key. Each contact's browser generates an RSA
keypair and registers only the public key. The owner confirms the key's
fingerprint out of band, then encrypts a copy of an item under a fresh per-share
key and wraps that key to each confirmed contact. The server stores the
ciphertext and wrapped keys and releases them only while a grant is active.
"""


def _decode(value: str, minimum: int, maximum: int, label: str) -> bytes:
    try:
        raw = base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError) as error:
        raise HTTPException(status_code=422, detail=f"{label} is not valid base64") from error
    if not minimum <= len(raw) <= maximum:
        raise HTTPException(status_code=422, detail=f"{label} has an unexpected size")
    return raw


def public_key_sha256(public_key: str) -> str:
    return hashlib.sha256(base64.b64decode(public_key)).hexdigest()


class ContactKey(BaseModel):
    public_key: str = Field(min_length=300, max_length=1400)


class ConfirmKey(BaseModel):
    public_key_sha256: str = Field(pattern="^[0-9a-f]{64}$")


class WrappedKey(BaseModel):
    wrapped_key: str = Field(min_length=1, max_length=2048)
    public_key_sha256: str = Field(pattern="^[0-9a-f]{64}$")


class SharePublish(BaseModel):
    ciphertext: str = Field(min_length=1, max_length=2_100_000)
    keys: dict[str, WrappedKey] = Field(max_length=20)


def owner_context(
    x_session_token: Optional[str] = Header(default=None),
    connection: Connection = Depends(database),
) -> tuple[str, Connection]:
    return user_from_session(connection, x_session_token), connection


def _owned_item(connection: Connection, owner_id: str, item_id: str) -> None:
    row = connection.execute(
        "SELECT id FROM vault_items WHERE id = ? AND owner_id = ?", (item_id, owner_id)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Vault item not found")


def register_routes(app) -> None:
    @app.put("/contact/key", tags=["key delivery"])
    def register_contact_key(
        request: ContactKey,
        auth: tuple[str, Connection] = Depends(contact_context),
    ) -> dict[str, str]:
        contact_id, connection = auth
        raw = _decode(request.public_key, 250, 1100, "Public key")
        if raw[:1] != b"\x30":
            raise HTTPException(status_code=422, detail="Public key must be DER SubjectPublicKeyInfo")
        contact = connection.execute(
            "SELECT owner_id, public_key FROM trusted_contacts WHERE id = ?", (contact_id,)
        ).fetchone()
        if contact["public_key"] == request.public_key:
            return {"status": "unchanged"}
        # A new key invalidates earlier confirmation and any keys wrapped to the old one.
        connection.execute(
            """
            UPDATE trusted_contacts
            SET public_key = ?, key_registered_at = ?, key_confirmed_at = NULL
            WHERE id = ?
            """,
            (request.public_key, utc_now().isoformat(), contact_id),
        )
        connection.execute("DELETE FROM share_keys WHERE contact_id = ?", (contact_id,))
        record_audit(connection, contact["owner_id"], "contact_key_registered", contact_id, contact_id)
        connection.commit()
        return {"status": "registered"}

    @app.post("/trusted-contacts/{contact_id}/key/confirm", tags=["key delivery"])
    def confirm_contact_key(
        contact_id: str,
        request: ConfirmKey,
        auth: tuple[str, Connection] = Depends(owner_context),
    ) -> dict[str, str]:
        owner_id, connection = auth
        contact = connection.execute(
            "SELECT public_key FROM trusted_contacts WHERE id = ? AND owner_id = ?",
            (contact_id, owner_id),
        ).fetchone()
        if contact is None:
            raise HTTPException(status_code=404, detail="Trusted contact not found")
        if not contact["public_key"]:
            raise HTTPException(status_code=409, detail="This contact has not set up a key yet")
        if not hmac.compare_digest(public_key_sha256(contact["public_key"]), request.public_key_sha256):
            raise HTTPException(
                status_code=409,
                detail="The contact's key changed. Review the new fingerprint before confirming.",
            )
        connection.execute(
            "UPDATE trusted_contacts SET key_confirmed_at = ? WHERE id = ?",
            (utc_now().isoformat(), contact_id),
        )
        record_audit(connection, owner_id, "contact_key_confirmed", contact_id, owner_id)
        connection.commit()
        return {"contact_id": contact_id, "status": "confirmed"}

    @app.put("/vault/items/{item_id}/share", tags=["key delivery"])
    def publish_share(
        item_id: str,
        request: SharePublish,
        auth: tuple[str, Connection] = Depends(owner_context),
    ) -> dict[str, list[str]]:
        owner_id, connection = auth
        _owned_item(connection, owner_id, item_id)
        policy = connection.execute(
            "SELECT id FROM access_policies WHERE vault_item_id = ? ORDER BY created_at DESC LIMIT 1",
            (item_id,),
        ).fetchone()
        if policy is None:
            raise HTTPException(status_code=409, detail="This item is not shared with anyone")
        allowed = {
            row["contact_id"]
            for row in connection.execute(
                "SELECT contact_id FROM policy_contacts WHERE policy_id = ?", (policy["id"],)
            )
        }
        for contact_id, key in request.keys.items():
            if contact_id not in allowed:
                raise HTTPException(status_code=422, detail="Contact is not part of this item's sharing rules")
            contact = connection.execute(
                "SELECT public_key, key_confirmed_at FROM trusted_contacts WHERE id = ? AND owner_id = ?",
                (contact_id, owner_id),
            ).fetchone()
            if contact is None or not contact["public_key"] or not contact["key_confirmed_at"]:
                raise HTTPException(status_code=409, detail="A contact's key has not been confirmed")
            if not hmac.compare_digest(public_key_sha256(contact["public_key"]), key.public_key_sha256):
                raise HTTPException(status_code=409, detail="A contact's key changed. Refresh and try again.")
            _decode(key.wrapped_key, 128, 1024, "Wrapped key")
        now = utc_now().isoformat()
        clear_item_shares(connection, item_id)
        connection.execute(
            "INSERT INTO item_shares (vault_item_id, ciphertext, updated_at) VALUES (?, ?, ?)",
            (item_id, request.ciphertext, now),
        )
        connection.executemany(
            "INSERT INTO share_keys (vault_item_id, contact_id, wrapped_key, created_at) VALUES (?, ?, ?, ?)",
            [(item_id, cid, key.wrapped_key, now) for cid, key in request.keys.items()],
        )
        record_audit(connection, owner_id, "item_share_published", item_id, owner_id)
        connection.commit()
        return {
            "delivered": sorted(request.keys),
            "pending": sorted(allowed - set(request.keys)),
        }

    @app.get("/vault/policies", tags=["key delivery"])
    def list_policies(
        auth: tuple[str, Connection] = Depends(owner_context),
    ) -> list[dict[str, object]]:
        owner_id, connection = auth
        rows = connection.execute(
            """
            SELECT p.id, p.vault_item_id, p.access_mode, p.required_approvals
            FROM access_policies p
            JOIN vault_items v ON v.id = p.vault_item_id
            WHERE v.owner_id = ?
            ORDER BY p.created_at
            """,
            (owner_id,),
        ).fetchall()
        result = []
        for row in rows:
            contact_ids = [
                r["contact_id"]
                for r in connection.execute(
                    "SELECT contact_id FROM policy_contacts WHERE policy_id = ? ORDER BY contact_id",
                    (row["id"],),
                )
            ]
            delivered = [
                r["contact_id"]
                for r in connection.execute(
                    "SELECT contact_id FROM share_keys WHERE vault_item_id = ? ORDER BY contact_id",
                    (row["vault_item_id"],),
                )
            ]
            result.append(
                {
                    "item_id": row["vault_item_id"],
                    "access_mode": row["access_mode"],
                    "required_approvals": row["required_approvals"],
                    "contact_ids": contact_ids,
                    "delivered_contact_ids": delivered,
                }
            )
        return result
