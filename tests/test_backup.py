from fastapi.testclient import TestClient

from trusted_access.main import app


def test_backup_export_is_explicitly_client_side(tmp_path) -> None:
    app.state.database_path = tmp_path / "backup.sqlite3"
    client = TestClient(app)
    token = client.post(
        "/auth/register",
        json={"email": "owner@example.com", "password": "correct horse battery"},
    ).json()["session_token"]
    client.post(
        "/vault/items",
        headers={"X-Session-Token": token},
        json={"category": "Medical", "title": "Allergies", "ciphertext": "ciphertext"},
    )

    response = client.get("/backup/export", headers={"X-Session-Token": token})

    assert response.status_code == 200
    assert response.json()["encryption"] == "client-side"
    assert "cannot recover lost keys" in response.json()["warning"]
    assert "ciphertext" in response.json()["encrypted_payload"]


def test_backup_import_does_not_claim_to_recover_or_decrypt(tmp_path) -> None:
    app.state.database_path = tmp_path / "backup-import.sqlite3"
    client = TestClient(app)
    token = client.post(
        "/auth/register",
        json={"email": "owner@example.com", "password": "correct horse battery"},
    ).json()["session_token"]

    response = client.post(
        "/backup/import",
        headers={"X-Session-Token": token},
        json={"format_version": 1, "encrypted_payload": "client-encrypted-payload"},
    )

    assert response.status_code == 202
    assert "Lost recovery keys cannot be recovered" in response.json()["message"]
