import sqlite3

from trusted_access.database import connect


def test_database_creates_workflow_tables(tmp_path) -> None:
    connection = connect(tmp_path / "trusted-access.sqlite3")

    tables = {
        row["name"]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }

    assert {
        "users",
        "trusted_contacts",
        "vault_items",
        "access_policies",
        "policy_contacts",
        "emergency_requests",
        "approvals",
        "access_grants",
        "audit_events",
    } <= tables


def test_database_enables_foreign_keys(tmp_path) -> None:
    connection = connect(tmp_path / "trusted-access.sqlite3")

    assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_database_rejects_orphan_vault_item(tmp_path) -> None:
    connection = connect(tmp_path / "trusted-access.sqlite3")

    try:
        connection.execute(
            """
            INSERT INTO vault_items
                (id, owner_id, category, title, ciphertext, created_at, updated_at)
            VALUES ('item', 'missing', 'Medical', 'Allergies', 'ciphertext', 'now', 'now')
            """
        )
    except sqlite3.IntegrityError:
        pass
    else:
        raise AssertionError("orphan vault item was accepted")


def test_connection_can_be_used_from_another_thread(tmp_path) -> None:
    import threading

    from trusted_access.database import connect

    connection = connect(tmp_path / "threads.sqlite3")
    errors = []

    def query() -> None:
        try:
            connection.execute("SELECT 1").fetchone()
        except Exception as error:  # pragma: no cover - failure path
            errors.append(error)

    thread = threading.Thread(target=query)
    thread.start()
    thread.join()
    connection.close()

    assert errors == []


def test_old_databases_are_migrated_with_key_delivery_columns(tmp_path) -> None:
    path = tmp_path / "old.sqlite3"
    legacy = sqlite3.connect(path)
    legacy.executescript(
        """
        CREATE TABLE users (id TEXT PRIMARY KEY, email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE trusted_contacts (id TEXT PRIMARY KEY,
            owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name TEXT NOT NULL, relationship TEXT NOT NULL,
            contact_method TEXT NOT NULL, created_at TEXT NOT NULL);
        INSERT INTO users VALUES ('u1', 'a@example.com', 'x', 'now');
        INSERT INTO trusted_contacts VALUES ('c1', 'u1', 'Old', 'Friend', 'x', 'now');
        """
    )
    legacy.commit()
    legacy.close()

    connection = connect(path)

    columns = {row["name"] for row in connection.execute("PRAGMA table_info(trusted_contacts)")}
    assert {"public_key", "key_registered_at", "key_confirmed_at"} <= columns
    row = connection.execute("SELECT name, public_key FROM trusted_contacts").fetchone()
    assert (row["name"], row["public_key"]) == ("Old", None)
    tables = {r["name"] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"item_shares", "share_keys"} <= tables
    connect(path)  # migrating twice is harmless
