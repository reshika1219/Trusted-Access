from fastapi.testclient import TestClient

from trusted_access.main import app


def register(client: TestClient, email: str) -> dict[str, str]:
    token = client.post(
        "/auth/register",
        json={"email": email, "password": "correct horse battery"},
    ).json()["session_token"]
    return {"X-Session-Token": token}


def make_item(client: TestClient, owner: dict[str, str], title: str = "Plan") -> str:
    return client.post(
        "/vault/items",
        headers=owner,
        json={"category": "Instructions", "title": title, "ciphertext": "v1:aa:bb"},
    ).json()["item_id"]


def make_contact(client: TestClient, owner: dict[str, str]) -> str:
    return client.post(
        "/trusted-contacts",
        headers=owner,
        json={"name": "Sam", "relationship": "Friend", "contact_method": "sam@example.com"},
    ).json()["contact_id"]


def test_owner_can_update_a_vault_item(tmp_path) -> None:
    app.state.database_path = tmp_path / "crud-update.sqlite3"
    client = TestClient(app)
    owner = register(client, "owner@example.com")
    item_id = make_item(client, owner)

    response = client.put(
        f"/vault/items/{item_id}",
        headers=owner,
        json={"category": "Medical", "title": "Renamed", "ciphertext": "v1:cc:dd"},
    )

    assert response.status_code == 200
    stored = client.get(f"/vault/items/{item_id}", headers=owner).json()
    assert (stored["category"], stored["title"], stored["ciphertext"]) == ("Medical", "Renamed", "v1:cc:dd")
    events = client.get("/audit-events", headers=owner).json()
    assert any(event["event_type"] == "vault_item_updated" for event in events)


def test_update_rejects_unknown_category_and_other_owners(tmp_path) -> None:
    app.state.database_path = tmp_path / "crud-update-auth.sqlite3"
    client = TestClient(app)
    owner = register(client, "owner@example.com")
    stranger = register(client, "stranger@example.com")
    item_id = make_item(client, owner)
    body = {"category": "Medical", "title": "Hijacked", "ciphertext": "v1:ee:ff"}

    assert client.put(f"/vault/items/{item_id}", headers=stranger, json=body).status_code == 404
    assert client.put(f"/vault/items/{item_id}", json=body).status_code == 401
    assert client.put(
        f"/vault/items/{item_id}", headers=owner, json={**body, "category": "Nonsense"}
    ).status_code == 422
    assert client.get(f"/vault/items/{item_id}", headers=owner).json()["title"] == "Plan"


def test_delete_item_ends_outstanding_access_and_is_audited(tmp_path) -> None:
    app.state.database_path = tmp_path / "crud-delete-item.sqlite3"
    client = TestClient(app)
    owner = register(client, "owner@example.com")
    item_id = make_item(client, owner)
    contact_id = make_contact(client, owner)
    contact_token = client.post(
        f"/trusted-contacts/{contact_id}/invite", headers=owner
    ).json()["contact_token"]
    client.put(
        f"/vault/items/{item_id}/policy",
        headers=owner,
        json={"access_mode": "emergency_only", "contact_ids": [contact_id], "required_approvals": 1},
    )
    request_id = client.post(
        "/access-requests", headers={"X-Contact-Token": contact_token}, json={"item_id": item_id}
    ).json()["request_id"]
    grant_id = client.post(f"/access-requests/{request_id}/approve", headers=owner).json()["grant_id"]
    assert client.get(f"/access-grants/{grant_id}", headers={"X-Contact-Token": contact_token}).status_code == 200

    assert client.delete(f"/vault/items/{item_id}", headers=owner).status_code == 200

    assert client.get(f"/vault/items/{item_id}", headers=owner).status_code == 404
    assert client.get(f"/access-grants/{grant_id}", headers={"X-Contact-Token": contact_token}).status_code == 404
    assert client.get("/access-requests", headers=owner).json() == []
    assert client.get("/access-grants", headers=owner).json() == []
    events = client.get("/audit-events", headers=owner).json()
    assert any(event["event_type"] == "vault_item_deleted" for event in events)


def test_delete_item_is_owner_only(tmp_path) -> None:
    app.state.database_path = tmp_path / "crud-delete-auth.sqlite3"
    client = TestClient(app)
    owner = register(client, "owner@example.com")
    stranger = register(client, "stranger@example.com")
    item_id = make_item(client, owner)

    assert client.delete(f"/vault/items/{item_id}", headers=stranger).status_code == 404
    assert client.delete(f"/vault/items/{item_id}").status_code == 401
    assert client.get(f"/vault/items/{item_id}", headers=owner).status_code == 200
    assert client.delete(f"/vault/items/{item_id}", headers=owner).status_code == 200
    assert client.delete(f"/vault/items/{item_id}", headers=owner).status_code == 404


def test_delete_contact_revokes_its_invite_and_access(tmp_path) -> None:
    app.state.database_path = tmp_path / "crud-delete-contact.sqlite3"
    client = TestClient(app)
    owner = register(client, "owner@example.com")
    stranger = register(client, "stranger@example.com")
    item_id = make_item(client, owner)
    contact_id = make_contact(client, owner)
    contact_token = client.post(
        f"/trusted-contacts/{contact_id}/invite", headers=owner
    ).json()["contact_token"]
    client.put(
        f"/vault/items/{item_id}/policy",
        headers=owner,
        json={"access_mode": "emergency_only", "contact_ids": [contact_id], "required_approvals": 1},
    )

    assert client.delete(f"/trusted-contacts/{contact_id}", headers=stranger).status_code == 404
    assert client.delete(f"/trusted-contacts/{contact_id}", headers=owner).status_code == 200

    assert client.get("/trusted-contacts", headers=owner).json() == []
    denied = client.post(
        "/access-requests", headers={"X-Contact-Token": contact_token}, json={"item_id": item_id}
    )
    assert denied.status_code == 401
    events = client.get("/audit-events", headers=owner).json()
    assert any(event["event_type"] == "trusted_contact_deleted" for event in events)
