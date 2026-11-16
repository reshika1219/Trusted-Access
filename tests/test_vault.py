from fastapi.testclient import TestClient

from trusted_access.main import app


def register(client: TestClient, email: str) -> str:
    response = client.post(
        "/auth/register",
        json={"email": email, "password": "correct horse battery"},
    )
    return response.json()["session_token"]


def test_vault_stores_and_returns_ciphertext_for_owner(tmp_path) -> None:
    app.state.database_path = tmp_path / "vault.sqlite3"
    client = TestClient(app)
    token = register(client, "owner@example.com")

    created = client.post(
        "/vault/items",
        headers={"X-Session-Token": token},
        json={
            "category": "Medical",
            "title": "Allergies",
            "ciphertext": "v1:authenticated-ciphertext",
        },
    )
    assert created.status_code == 201
    item_id = created.json()["item_id"]

    item = client.get(
        f"/vault/items/{item_id}", headers={"X-Session-Token": token}
    )
    assert item.status_code == 200
    assert item.json()["ciphertext"] == "v1:authenticated-ciphertext"


def test_vault_rejects_unauthorized_access_and_categories(tmp_path) -> None:
    app.state.database_path = tmp_path / "vault.sqlite3"
    client = TestClient(app)
    owner_token = register(client, "owner@example.com")
    other_token = register(client, "other@example.com")

    invalid = client.post(
        "/vault/items",
        headers={"X-Session-Token": owner_token},
        json={"category": "Passwords", "title": "Secrets", "ciphertext": "data"},
    )
    assert invalid.status_code == 422

    created = client.post(
        "/vault/items",
        headers={"X-Session-Token": owner_token},
        json={"category": "Medical", "title": "Allergies", "ciphertext": "data"},
    )
    item_id = created.json()["item_id"]
    assert client.get(
        f"/vault/items/{item_id}", headers={"X-Session-Token": other_token}
    ).status_code == 404


def test_vault_requires_session(tmp_path) -> None:
    app.state.database_path = tmp_path / "vault.sqlite3"
    client = TestClient(app)

    assert client.get("/vault/items").status_code == 401
