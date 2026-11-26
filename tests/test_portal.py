from fastapi.testclient import TestClient

from trusted_access.main import app


def build(client: TestClient):
    owner = {"X-Session-Token": client.post(
        "/auth/register", json={"email": "owner@example.com", "password": "correct horse battery"}
    ).json()["session_token"]}
    contacts, tokens = [], []
    for name in ("Ana", "Ben", "Cy"):
        contact_id = client.post(
            "/trusted-contacts", headers=owner,
            json={"name": name, "relationship": "Friend", "contact_method": f"{name}@example.com"},
        ).json()["contact_id"]
        contacts.append(contact_id)
        tokens.append({"X-Contact-Token": client.post(
            f"/trusted-contacts/{contact_id}/invite", headers=owner
        ).json()["contact_token"]})
    shared = client.post("/vault/items", headers=owner, json={
        "category": "Medical", "title": "Shared plan", "ciphertext": "v1:SECRET:SECRET"}).json()["item_id"]
    private = client.post("/vault/items", headers=owner, json={
        "category": "Documents", "title": "Private diary", "ciphertext": "v1:HIDDEN:HIDDEN"}).json()["item_id"]
    client.put(f"/vault/items/{shared}/policy", headers=owner, json={
        "access_mode": "emergency_only", "contact_ids": contacts[:2], "required_approvals": 2})
    return owner, contacts, tokens, shared, private


def test_contact_sees_only_shared_item_metadata_never_ciphertext(tmp_path) -> None:
    app.state.database_path = tmp_path / "portal-items.sqlite3"
    client = TestClient(app)
    _, _, tokens, shared, private = build(client)

    profile = client.get("/contact/me", headers=tokens[0]).json()
    assert profile["name"] == "Ana"
    items = client.get("/contact/items", headers=tokens[0]).json()
    assert [item["id"] for item in items] == [shared]
    assert items[0]["title"] == "Shared plan"
    assert items[0]["required_approvals"] == 2
    assert "ciphertext" not in items[0]
    assert "SECRET" not in client.get("/contact/items", headers=tokens[0]).text
    assert "Private diary" not in client.get("/contact/items", headers=tokens[0]).text
    # A contact outside the policy sees nothing.
    assert client.get("/contact/items", headers=tokens[2]).json() == []


def test_contact_portal_requires_a_contact_token(tmp_path) -> None:
    app.state.database_path = tmp_path / "portal-auth.sqlite3"
    client = TestClient(app)
    owner, *_ = build(client)

    for path in ("/contact/me", "/contact/items", "/contact/requests"):
        assert client.get(path).status_code == 401
        assert client.get(path, headers={"X-Contact-Token": "bogus"}).status_code == 401
        # An owner session token is not a contact token.
        assert client.get(path, headers={"X-Contact-Token": owner["X-Session-Token"]}).status_code == 401


def test_request_lifecycle_is_visible_to_requester_and_approvers(tmp_path) -> None:
    app.state.database_path = tmp_path / "portal-requests.sqlite3"
    client = TestClient(app)
    owner, _, tokens, shared, _ = build(client)
    request_id = client.post("/access-requests", headers=tokens[0], json={"item_id": shared}).json()["request_id"]

    mine = client.get("/contact/requests", headers=tokens[0]).json()
    assert [r["id"] for r in mine["mine"]] == [request_id]
    assert mine["mine"][0]["status"] == "pending"
    assert mine["mine"][0]["approvals"] == 0 and mine["mine"][0]["required_approvals"] == 2
    assert mine["mine"][0]["grant_active"] is False
    assert mine["to_approve"] == []  # a requester never approves their own request

    ben = client.get("/contact/requests", headers=tokens[1]).json()
    assert ben["mine"] == []
    assert [r["id"] for r in ben["to_approve"]] == [request_id]
    assert ben["to_approve"][0]["requester_name"] == "Ana"
    assert client.get("/contact/requests", headers=tokens[2]).json() == {"mine": [], "to_approve": []}

    assert client.post(f"/access-requests/{request_id}/contact-approve", headers=tokens[1]).status_code == 200
    assert client.get("/contact/requests", headers=tokens[1]).json()["to_approve"] == []

    client.post(f"/access-requests/{request_id}/approve", headers=owner)
    final = client.get("/contact/requests", headers=tokens[0]).json()["mine"][0]
    assert final["approvals"] == 1


def test_active_grant_is_reported_and_revocation_is_reflected(tmp_path) -> None:
    app.state.database_path = tmp_path / "portal-grant.sqlite3"
    client = TestClient(app)
    owner, contacts, tokens, _, _ = build(client)
    single = client.post("/vault/items", headers=owner, json={
        "category": "Pets", "title": "Pet care", "ciphertext": "v1:aa:bb"}).json()["item_id"]
    client.put(f"/vault/items/{single}/policy", headers=owner, json={
        "access_mode": "emergency_only", "contact_ids": contacts[:2], "required_approvals": 1})
    request_id = client.post("/access-requests", headers=tokens[0], json={"item_id": single}).json()["request_id"]
    assert client.get("/contact/requests", headers=tokens[0]).json()["mine"][0]["grant_active"] is False

    grant_id = client.post(f"/access-requests/{request_id}/approve", headers=owner).json()["grant_id"]
    mine = client.get("/contact/requests", headers=tokens[0]).json()["mine"][0]
    assert mine["grant_active"] is True and mine["grant_id"] == grant_id
    assert mine["grant_expires_at"]
    assert client.get("/contact/requests", headers=tokens[1]).json()["to_approve"] == []

    client.post(f"/access-grants/{grant_id}/revoke", headers=owner)
    revoked = client.get("/contact/requests", headers=tokens[0]).json()["mine"][0]
    assert revoked["grant_active"] is False and revoked["grant_revoked_at"]
