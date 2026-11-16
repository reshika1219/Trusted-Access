from fastapi.testclient import TestClient

from trusted_access.main import app


def test_permitted_contact_can_request_item(tmp_path) -> None:
    app.state.database_path = tmp_path / "requests.sqlite3"
    client = TestClient(app)
    owner_token = client.post(
        "/auth/register",
        json={"email": "owner@example.com", "password": "correct horse battery"},
    ).json()["session_token"]
    contact_id = client.post(
        "/trusted-contacts",
        headers={"X-Session-Token": owner_token},
        json={
            "name": "Trusted Person",
            "relationship": "Sibling",
            "contact_method": "sibling@example.com",
        },
    ).json()["contact_id"]
    contact_token = client.post(
        f"/trusted-contacts/{contact_id}/invite",
        headers={"X-Session-Token": owner_token},
    ).json()["contact_token"]
    item_id = client.post(
        "/vault/items",
        headers={"X-Session-Token": owner_token},
        json={"category": "Medical", "title": "Allergies", "ciphertext": "ciphertext"},
    ).json()["item_id"]
    client.put(
        f"/vault/items/{item_id}/policy",
        headers={"X-Session-Token": owner_token},
        json={
            "access_mode": "emergency_only",
            "contact_ids": [contact_id],
            "required_approvals": 1,
        },
    )

    request = client.post(
        "/access-requests",
        headers={"X-Contact-Token": contact_token},
        json={"item_id": item_id},
    )
    assert request.status_code == 201
    assert request.json()["status"] == "pending"


def test_unpermitted_contact_cannot_request_item(tmp_path) -> None:
    app.state.database_path = tmp_path / "requests.sqlite3"
    client = TestClient(app)
    owner_token = client.post(
        "/auth/register",
        json={"email": "owner@example.com", "password": "correct horse battery"},
    ).json()["session_token"]
    contact_id = client.post(
        "/trusted-contacts",
        headers={"X-Session-Token": owner_token},
        json={
            "name": "Trusted Person",
            "relationship": "Sibling",
            "contact_method": "sibling@example.com",
        },
    ).json()["contact_id"]
    contact_token = client.post(
        f"/trusted-contacts/{contact_id}/invite",
        headers={"X-Session-Token": owner_token},
    ).json()["contact_token"]
    item_id = client.post(
        "/vault/items",
        headers={"X-Session-Token": owner_token},
        json={"category": "Medical", "title": "Allergies", "ciphertext": "ciphertext"},
    ).json()["item_id"]

    assert client.post(
        "/access-requests",
        headers={"X-Contact-Token": contact_token},
        json={"item_id": item_id},
    ).status_code == 403
