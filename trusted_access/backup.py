from __future__ import annotations

import json
from sqlite3 import Connection
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel, Field

from trusted_access.auth import user_from_session, utc_now
from trusted_access.main import database
from trusted_access.vault import record_audit


class EncryptedBackup(BaseModel):
    format_version: int = Field(default=1, ge=1, le=1)
    encrypted_payload: str = Field(min_length=1, max_length=50_000_000)


def owner_context(
    x_session_token: Optional[str] = Header(default=None),
    connection: Connection = Depends(database),
) -> tuple[str, Connection]:
    return user_from_session(connection, x_session_token), connection


def register_routes(app) -> None:
    @app.get("/backup/export", tags=["recovery"])
    def export_backup(
        auth: tuple[str, Connection] = Depends(owner_context),
    ) -> dict[str, object]:
        owner_id, connection = auth
        items = [
            dict(row)
            for row in connection.execute(
                """
                SELECT id, category, title, ciphertext, created_at, updated_at
                FROM vault_items WHERE owner_id = ? ORDER BY id
                """,
                (owner_id,),
            ).fetchall()
        ]
        contacts = [
            dict(row)
            for row in connection.execute(
                """
                SELECT id, name, relationship, contact_method, created_at
                FROM trusted_contacts WHERE owner_id = ? ORDER BY id
                """,
                (owner_id,),
            ).fetchall()
        ]
        record_audit(connection, owner_id, "backup_exported", owner_id, owner_id)
        connection.commit()
        return {
            "format_version": 1,
            "encryption": "client-side",
            "warning": "Protect this export with your recovery key. The server cannot recover lost keys.",
            "encrypted_payload": json.dumps({"vault_items": items, "trusted_contacts": contacts}),
        }

    @app.post("/backup/import", status_code=status.HTTP_202_ACCEPTED, tags=["recovery"])
    def import_backup(
        backup: EncryptedBackup,
        auth: tuple[str, Connection] = Depends(owner_context),
    ) -> dict[str, str]:
        owner_id, connection = auth
        if not backup.encrypted_payload.strip():
            raise HTTPException(status_code=422, detail="Encrypted backup payload is empty")
        record_audit(connection, owner_id, "backup_import_requested", owner_id, owner_id)
        connection.commit()
        return {
            "status": "accepted",
            "message": (
                "The client must decrypt and validate this payload before records are imported. "
                "Lost recovery keys cannot be recovered by the server."
            ),
        }
