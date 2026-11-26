from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    token_hash TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS contact_sessions (
    token_hash TEXT PRIMARY KEY,
    contact_id TEXT NOT NULL REFERENCES trusted_contacts(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS trusted_contacts (
    id TEXT PRIMARY KEY,
    owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    relationship TEXT NOT NULL,
    contact_method TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS vault_items (
    id TEXT PRIMARY KEY,
    owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    ciphertext TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS access_policies (
    id TEXT PRIMARY KEY,
    vault_item_id TEXT NOT NULL REFERENCES vault_items(id) ON DELETE CASCADE,
    access_mode TEXT NOT NULL,
    required_approvals INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS policy_contacts (
    policy_id TEXT NOT NULL REFERENCES access_policies(id) ON DELETE CASCADE,
    contact_id TEXT NOT NULL REFERENCES trusted_contacts(id) ON DELETE CASCADE,
    PRIMARY KEY (policy_id, contact_id)
);

CREATE TABLE IF NOT EXISTS emergency_requests (
    id TEXT PRIMARY KEY,
    vault_item_id TEXT NOT NULL REFERENCES vault_items(id) ON DELETE CASCADE,
    requester_contact_id TEXT NOT NULL REFERENCES trusted_contacts(id) ON DELETE CASCADE,
    status TEXT NOT NULL,
    requested_at TEXT NOT NULL,
    expires_at TEXT
);

CREATE TABLE IF NOT EXISTS approvals (
    id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL REFERENCES emergency_requests(id) ON DELETE CASCADE,
    contact_id TEXT NOT NULL REFERENCES trusted_contacts(id) ON DELETE CASCADE,
    decision TEXT NOT NULL,
    decided_at TEXT NOT NULL,
    UNIQUE (request_id, contact_id)
);

CREATE TABLE IF NOT EXISTS access_grants (
    id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL REFERENCES emergency_requests(id) ON DELETE CASCADE,
    vault_item_id TEXT NOT NULL REFERENCES vault_items(id) ON DELETE CASCADE,
    recipient_contact_id TEXT NOT NULL REFERENCES trusted_contacts(id) ON DELETE CASCADE,
    expires_at TEXT NOT NULL,
    revoked_at TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_events (
    id TEXT PRIMARY KEY,
    owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    actor_id TEXT,
    resource_id TEXT,
    metadata_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def connect(database_path: Path) -> sqlite3.Connection:
    # Each request owns its connection, but FastAPI may resolve its sync
    # dependencies on different worker threads, so allow cross-thread use.
    connection = sqlite3.connect(database_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA)
    return connection
