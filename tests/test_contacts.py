from fastapi.testclient import TestClient

from trusted_access.main import app


def test_contacts_do_not_receive_access_automatically(tmp_path) -> None:
    app.state.database_path = tmp_path / "contacts.sqlite3"
    client = TestClient(app)
    token = client.post(
        "/auth/register",
        json={"email": "owner@example.com", "password": "correct horse battery"},
    ).json()["session_token"]

    created = client.post(
        "/trusted-contacts",
        headers={"X-Session-Token": token},
        json={
            "name": "Trusted Person",
            "relationship": "Sibling",
            "contact_method": "sibling@example.com",
        },
    )
    assert created.status_code == 201
    contacts = client.get(
        "/trusted-contacts", headers={"X-Session-Token": token}
    ).json()
    assert len(contacts) == 1
    assert contacts[0]["name"] == "Trusted Person"


def test_policy_requires_owned_contacts_and_supports_threshold(tmp_path) -> None:
    app.state.database_path = tmp_path / "policies.sqlite3"
    client = TestClient(app)
    token = client.post(
        "/auth/register",
        json={"email": "owner@example.com", "password": "correct horse battery"},
    ).json()["session_token"]
    contacts = []
    for index in range(3):
        contacts.append(
            client.post(
                "/trusted-contacts",
                headers={"X-Session-Token": token},
                json={
                    "name": f"Trusted {index}",
                    "relationship": "Friend",
                    "contact_method": f"friend{index}@example.com",
                },
            ).json()["contact_id"]
        )
    item_id = client.post(
        "/vault/items",
        headers={"X-Session-Token": token},
        json={"category": "Instructions", "title": "Plan", "ciphertext": "data"},
    ).json()["item_id"]

    policy = client.put(
        f"/vault/items/{item_id}/policy",
        headers={"X-Session-Token": token},
        json={
            "access_mode": "emergency_only",
            "contact_ids": contacts,
            "required_approvals": 2,
        },
    )
    assert policy.status_code == 200

    invalid = client.put(
        f"/vault/items/{item_id}/policy",
        headers={"X-Session-Token": token},
        json={
            "access_mode": "emergency_only",
            "contact_ids": ["not-owned"],
            "required_approvals": 1,
        },
    )
    assert invalid.status_code == 422
