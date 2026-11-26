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
