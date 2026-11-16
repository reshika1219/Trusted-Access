from fastapi.testclient import TestClient

from trusted_access.main import app


def test_owner_approval_creates_expiring_read_only_grant(tmp_path) -> None:
    app.state.database_path = tmp_path / "access.sqlite3"
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
    request_id = client.post(
        "/access-requests",
        headers={"X-Contact-Token": contact_token},
        json={"item_id": item_id},
    ).json()["request_id"]

    pending = client.get(
        "/access-requests", headers={"X-Session-Token": owner_token}
    )
    assert pending.status_code == 200
    assert pending.json()[0]["status"] == "pending"

    approved = client.post(
        f"/access-requests/{request_id}/approve",
        headers={"X-Session-Token": owner_token},
    )
    assert approved.status_code == 200
    grant_id = approved.json()["grant_id"]

    viewed = client.get(
        f"/access-grants/{grant_id}", headers={"X-Contact-Token": contact_token}
    )
    assert viewed.status_code == 200
    assert viewed.json()["ciphertext"] == "ciphertext"
