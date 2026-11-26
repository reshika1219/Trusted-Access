from fastapi.testclient import TestClient

from trusted_access.main import app


def setup_case(client: TestClient, threshold: int = 1):
    owner_token = client.post(
        "/auth/register",
        json={"email": "owner@example.com", "password": "correct horse battery"},
    ).json()["session_token"]
    contacts = []
    tokens = []
    for index in range(3):
        contact_id = client.post(
            "/trusted-contacts",
            headers={"X-Session-Token": owner_token},
            json={
                "name": f"Trusted {index}",
                "relationship": "Friend",
                "contact_method": f"friend{index}@example.com",
            },
        ).json()["contact_id"]
        contacts.append(contact_id)
        tokens.append(
            client.post(
                f"/trusted-contacts/{contact_id}/invite",
                headers={"X-Session-Token": owner_token},
            ).json()["contact_token"]
        )
    item_id = client.post(
        "/vault/items",
        headers={"X-Session-Token": owner_token},
        json={"category": "Instructions", "title": "Plan", "ciphertext": "ciphertext"},
    ).json()["item_id"]
    client.put(
        f"/vault/items/{item_id}/policy",
        headers={"X-Session-Token": owner_token},
        json={
            "access_mode": "emergency_only",
            "contact_ids": contacts,
            "required_approvals": threshold,
        },
    )
    request_id = client.post(
        "/access-requests",
        headers={"X-Contact-Token": tokens[0]},
        json={"item_id": item_id},
    ).json()["request_id"]
    return owner_token, contacts, tokens, request_id


def test_two_of_three_contacts_must_approve(tmp_path) -> None:
    app.state.database_path = tmp_path / "multi-party.sqlite3"
    client = TestClient(app)
    owner_token, _, tokens, request_id = setup_case(client, threshold=2)

    owner_approval = client.post(
        f"/access-requests/{request_id}/approve",
        headers={"X-Session-Token": owner_token},
    )
    assert owner_approval.json()["status"] == "awaiting_contact_approvals"

    first = client.post(
        f"/access-requests/{request_id}/contact-approve",
        headers={"X-Contact-Token": tokens[0]},
    )
    assert first.json()["status"] == "awaiting_more_approvals"
    second = client.post(
        f"/access-requests/{request_id}/contact-approve",
        headers={"X-Contact-Token": tokens[1]},
    )
    assert second.status_code == 200
    assert second.json()["grant_id"]


def test_owner_can_revoke_grant_and_audit_is_visible(tmp_path) -> None:
    app.state.database_path = tmp_path / "revoke.sqlite3"
    client = TestClient(app)
    owner_token, _, tokens, request_id = setup_case(client)
    grant_id = client.post(
        f"/access-requests/{request_id}/approve",
        headers={"X-Session-Token": owner_token},
    ).json()["grant_id"]

    revoked = client.post(
        f"/access-grants/{grant_id}/revoke",
        headers={"X-Session-Token": owner_token},
    )
    assert revoked.status_code == 200
    assert client.get(
        f"/access-grants/{grant_id}", headers={"X-Contact-Token": tokens[0]}
    ).status_code == 403
    events = client.get(
        "/audit-events", headers={"X-Session-Token": owner_token}
    ).json()
    assert any(event["event_type"] == "access_revoked" for event in events)


def test_owner_lists_only_their_own_grants_with_revocation_state(tmp_path) -> None:
    app.state.database_path = tmp_path / "grant-list.sqlite3"
    client = TestClient(app)
    owner_token, _, _, request_id = setup_case(client)
    grant_id = client.post(
        f"/access-requests/{request_id}/approve",
        headers={"X-Session-Token": owner_token},
    ).json()["grant_id"]
    other_token = client.post(
        "/auth/register",
        json={"email": "other@example.com", "password": "correct horse battery"},
    ).json()["session_token"]

    listed = client.get("/access-grants", headers={"X-Session-Token": owner_token}).json()
    assert [grant["id"] for grant in listed] == [grant_id]
    assert listed[0]["request_id"] == request_id
    assert listed[0]["revoked_at"] is None
    assert client.get("/access-grants", headers={"X-Session-Token": other_token}).json() == []
    assert client.get("/access-grants").status_code == 401

    client.post(f"/access-grants/{grant_id}/revoke", headers={"X-Session-Token": owner_token})
    revoked = client.get("/access-grants", headers={"X-Session-Token": owner_token}).json()
    assert revoked[0]["revoked_at"] is not None
