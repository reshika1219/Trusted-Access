from fastapi.testclient import TestClient

from trusted_access.main import app


def setup(client: TestClient, contact_count: int = 3):
    owner = {"X-Session-Token": client.post(
        "/auth/register", json={"email": "owner@example.com", "password": "correct horse battery"}
    ).json()["session_token"]}
    contacts, tokens = [], []
    for name in range(contact_count):
        contact_id = client.post(
            "/trusted-contacts", headers=owner,
            json={"name": f"C{name}", "relationship": "Friend", "contact_method": "x"},
        ).json()["contact_id"]
        contacts.append(contact_id)
        tokens.append({"X-Contact-Token": client.post(
            f"/trusted-contacts/{contact_id}/invite", headers=owner
        ).json()["contact_token"]})
    item = client.post("/vault/items", headers=owner, json={
        "category": "Pets", "title": "Item", "ciphertext": "v1:aa:bb"}).json()["item_id"]
    return owner, contacts, tokens, item


def put(client, owner, item, contact_ids, approvals=1, mode="emergency_only"):
    return client.put(f"/vault/items/{item}/policy", headers=owner, json={
        "access_mode": mode, "contact_ids": contact_ids, "required_approvals": approvals})


def test_saving_a_policy_replaces_the_previous_one(tmp_path) -> None:
    app.state.database_path = tmp_path / "policy-replace.sqlite3"
    client = TestClient(app)
    owner, contacts, tokens, item = setup(client)
    assert put(client, owner, item, contacts[:2], approvals=2).status_code == 200
    assert put(client, owner, item, [contacts[1]], approvals=1).status_code == 200

    removed = client.post("/access-requests", headers=tokens[0], json={"item_id": item})
    assert removed.status_code == 403
    assert client.get("/contact/items", headers=tokens[0]).json() == []
    assert len(client.get("/contact/items", headers=tokens[1]).json()) == 1
    # The newest threshold (1) is the one that applies.
    request_id = client.post("/access-requests", headers=tokens[1], json={"item_id": item}).json()["request_id"]
    assert "grant_id" in client.post(f"/access-requests/{request_id}/approve", headers=owner).json()


def test_narrowing_a_policy_ends_access_for_removed_contacts_only(tmp_path) -> None:
    app.state.database_path = tmp_path / "policy-narrow.sqlite3"
    client = TestClient(app)
    owner, contacts, tokens, item = setup(client)
    put(client, owner, item, contacts[:3])
    granted = client.post("/access-requests", headers=tokens[0], json={"item_id": item}).json()["request_id"]
    grant_id = client.post(f"/access-requests/{granted}/approve", headers=owner).json()["grant_id"]
    pending_removed = client.post("/access-requests", headers=tokens[1], json={"item_id": item}).json()["request_id"]
    pending_kept = client.post("/access-requests", headers=tokens[2], json={"item_id": item}).json()["request_id"]
    assert client.get(f"/access-grants/{grant_id}", headers=tokens[0]).status_code == 200

    put(client, owner, item, [contacts[2]])

    assert client.get(f"/access-grants/{grant_id}", headers=tokens[0]).status_code == 403
    statuses = {r["id"]: r["status"] for r in client.get("/access-requests", headers=owner).json()}
    assert statuses[pending_removed] == "rejected"
    assert statuses[pending_kept] == "pending"
    events = {e["event_type"] for e in client.get("/audit-events", headers=owner).json()}
    assert {"access_revoked", "access_rejected", "access_policy_changed"} <= events


def test_owner_can_read_the_current_policy(tmp_path) -> None:
    app.state.database_path = tmp_path / "policy-read.sqlite3"
    client = TestClient(app)
    owner, contacts, _, item = setup(client)
    stranger = {"X-Session-Token": client.post(
        "/auth/register", json={"email": "stranger@example.com", "password": "correct horse battery"}
    ).json()["session_token"]}

    assert client.get(f"/vault/items/{item}/policy", headers=owner).json() == {"policy": None}
    put(client, owner, item, contacts[:2], approvals=2, mode="time_limited")
    policy = client.get(f"/vault/items/{item}/policy", headers=owner).json()["policy"]
    assert policy["access_mode"] == "time_limited"
    assert policy["required_approvals"] == 2
    assert sorted(policy["contact_ids"]) == sorted(contacts[:2])
    assert client.get(f"/vault/items/{item}/policy", headers=stranger).status_code == 404
    assert client.get(f"/vault/items/{item}/policy").status_code == 401


def test_stop_sharing_removes_rules_requests_and_grants(tmp_path) -> None:
    app.state.database_path = tmp_path / "policy-delete.sqlite3"
    client = TestClient(app)
    owner, contacts, tokens, item = setup(client)
    stranger = {"X-Session-Token": client.post(
        "/auth/register", json={"email": "stranger@example.com", "password": "correct horse battery"}
    ).json()["session_token"]}
    put(client, owner, item, contacts)
    granted = client.post("/access-requests", headers=tokens[0], json={"item_id": item}).json()["request_id"]
    grant_id = client.post(f"/access-requests/{granted}/approve", headers=owner).json()["grant_id"]
    waiting = client.post("/access-requests", headers=tokens[1], json={"item_id": item}).json()["request_id"]

    assert client.delete(f"/vault/items/{item}/policy", headers=stranger).status_code == 404
    assert client.delete(f"/vault/items/{item}/policy").status_code == 401
    assert client.delete(f"/vault/items/{item}/policy", headers=owner).json()["status"] == "not_shared"

    assert client.get(f"/access-grants/{grant_id}", headers=tokens[0]).status_code == 403
    assert {r["id"]: r["status"] for r in client.get("/access-requests", headers=owner).json()}[waiting] == "rejected"
    assert client.get(f"/vault/items/{item}/policy", headers=owner).json() == {"policy": None}
    assert client.get("/contact/items", headers=tokens[2]).json() == []
    assert client.post("/access-requests", headers=tokens[2], json={"item_id": item}).status_code == 403
    events = {e["event_type"] for e in client.get("/audit-events", headers=owner).json()}
    assert "access_policy_removed" in events
