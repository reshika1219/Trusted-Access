import base64
import hashlib
import os

from fastapi.testclient import TestClient

from trusted_access.main import app


def fake_spki() -> str:
    # The server only checks structure (DER SEQUENCE, plausible size); real key
    # material is generated and used in the browser.
    return base64.b64encode(b"\x30" + os.urandom(421)).decode()


def sha(public_key: str) -> str:
    return hashlib.sha256(base64.b64decode(public_key)).hexdigest()


def wrapped() -> str:
    return base64.b64encode(os.urandom(384)).decode()


class Case:
    def __init__(self, client: TestClient, contacts: int = 2) -> None:
        self.client = client
        self.owner = {"X-Session-Token": client.post(
            "/auth/register", json={"email": "owner@example.com", "password": "correct horse battery"}
        ).json()["session_token"]}
        self.ids, self.tokens, self.keys = [], [], []
        for index in range(contacts):
            cid = client.post("/trusted-contacts", headers=self.owner, json={
                "name": f"C{index}", "relationship": "Friend", "contact_method": "x"}).json()["contact_id"]
            self.ids.append(cid)
            self.tokens.append({"X-Contact-Token": client.post(
                f"/trusted-contacts/{cid}/invite", headers=self.owner).json()["contact_token"]})
            self.keys.append(fake_spki())
        self.item = client.post("/vault/items", headers=self.owner, json={
            "category": "Pets", "title": "Item", "ciphertext": "v1:aa:bb"}).json()["item_id"]

    def register(self, index: int):
        return self.client.put("/contact/key", headers=self.tokens[index], json={"public_key": self.keys[index]})

    def confirm(self, index: int):
        return self.client.post(f"/trusted-contacts/{self.ids[index]}/key/confirm", headers=self.owner,
                                json={"public_key_sha256": sha(self.keys[index])})

    def share_policy(self, indexes=(0, 1), approvals=1):
        return self.client.put(f"/vault/items/{self.item}/policy", headers=self.owner, json={
            "access_mode": "emergency_only", "contact_ids": [self.ids[i] for i in indexes],
            "required_approvals": approvals})

    def publish(self, indexes, ciphertext="v1:share:blob"):
        return self.client.put(f"/vault/items/{self.item}/share", headers=self.owner, json={
            "ciphertext": ciphertext,
            "keys": {self.ids[i]: {"wrapped_key": wrapped(), "public_key_sha256": sha(self.keys[i])} for i in indexes}})

    def ready(self, indexes=(0, 1)):
        for i in indexes:
            assert self.register(i).status_code == 200
            assert self.confirm(i).status_code == 200
        assert self.share_policy(indexes).status_code == 200


def test_contact_registers_a_public_key_and_owner_sees_it_unconfirmed(tmp_path) -> None:
    app.state.database_path = tmp_path / "keys-register.sqlite3"
    client = TestClient(app)
    case = Case(client)

    assert client.get("/contact/me", headers=case.tokens[0]).json()["public_key"] is None
    assert case.register(0).json() == {"status": "registered"}
    assert case.register(0).json() == {"status": "unchanged"}

    me = client.get("/contact/me", headers=case.tokens[0]).json()
    assert me["public_key"] == case.keys[0] and me["key_confirmed"] is False
    listed = {c["id"]: c for c in client.get("/trusted-contacts", headers=case.owner).json()}
    assert listed[case.ids[0]]["public_key"] == case.keys[0]
    assert listed[case.ids[0]]["key_confirmed"] is False
    assert listed[case.ids[1]]["public_key"] is None
    events = {e["event_type"] for e in client.get("/audit-events", headers=case.owner).json()}
    assert "contact_key_registered" in events


def test_key_registration_is_validated_and_contact_only(tmp_path) -> None:
    app.state.database_path = tmp_path / "keys-validate.sqlite3"
    client = TestClient(app)
    case = Case(client)

    assert client.put("/contact/key", json={"public_key": case.keys[0]}).status_code == 401
    assert client.put("/contact/key", headers=case.owner, json={"public_key": case.keys[0]}).status_code == 401
    for bad in ("!" * 400, "A" * 400, base64.b64encode(b"\x31" + os.urandom(421)).decode(), "QUJD"):
        assert client.put("/contact/key", headers=case.tokens[0], json={"public_key": bad}).status_code == 422


def test_only_the_owner_can_confirm_and_only_the_exact_key(tmp_path) -> None:
    app.state.database_path = tmp_path / "keys-confirm.sqlite3"
    client = TestClient(app)
    case = Case(client)
    stranger = {"X-Session-Token": client.post(
        "/auth/register", json={"email": "stranger@example.com", "password": "correct horse battery"}
    ).json()["session_token"]}

    assert case.confirm(0).status_code == 409  # no key registered yet
    case.register(0)
    wrong = client.post(f"/trusted-contacts/{case.ids[0]}/key/confirm", headers=case.owner,
                        json={"public_key_sha256": sha(fake_spki())})
    assert wrong.status_code == 409 and "changed" in wrong.json()["detail"]
    assert client.post(f"/trusted-contacts/{case.ids[0]}/key/confirm", headers=stranger,
                       json={"public_key_sha256": sha(case.keys[0])}).status_code == 404
    assert client.post(f"/trusted-contacts/{case.ids[0]}/key/confirm",
                       json={"public_key_sha256": sha(case.keys[0])}).status_code == 401
    assert client.post(f"/trusted-contacts/{case.ids[0]}/key/confirm", headers=case.owner,
                       json={"public_key_sha256": "nothex"}).status_code == 422

    assert case.confirm(0).status_code == 200
    assert client.get("/contact/me", headers=case.tokens[0]).json()["key_confirmed"] is True
    events = {e["event_type"] for e in client.get("/audit-events", headers=case.owner).json()}
    assert "contact_key_confirmed" in events


def test_a_replaced_key_loses_confirmation_and_wrapped_keys(tmp_path) -> None:
    app.state.database_path = tmp_path / "keys-replace.sqlite3"
    client = TestClient(app)
    case = Case(client)
    case.ready()
    assert case.publish([0, 1]).status_code == 200

    case.keys[0] = fake_spki()  # an attacker with a stolen invite registers their own key
    assert case.register(0).json() == {"status": "registered"}

    assert client.get("/contact/me", headers=case.tokens[0]).json()["key_confirmed"] is False
    policies = client.get("/vault/policies", headers=case.owner).json()
    assert policies[0]["delivered_contact_ids"] == [case.ids[1]]
    # Publishing to the unconfirmed replacement key is refused.
    assert case.publish([0]).status_code == 409


def test_publish_share_enforces_policy_and_confirmed_current_keys(tmp_path) -> None:
    app.state.database_path = tmp_path / "keys-publish.sqlite3"
    client = TestClient(app)
    case = Case(client, contacts=3)
    stranger = {"X-Session-Token": client.post(
        "/auth/register", json={"email": "stranger@example.com", "password": "correct horse battery"}
    ).json()["session_token"]}
    for i in range(3):
        case.register(i)

    assert case.publish([0]).status_code == 409  # not shared yet
    case.share_policy((0, 1))
    assert case.publish([0]).status_code == 409  # key not confirmed
    case.confirm(0)
    case.confirm(1)
    case.confirm(2)
    assert case.publish([2]).status_code == 422  # not in this item's policy
    stale = client.put(f"/vault/items/{case.item}/share", headers=case.owner, json={
        "ciphertext": "x", "keys": {case.ids[0]: {"wrapped_key": wrapped(), "public_key_sha256": sha(fake_spki())}}})
    assert stale.status_code == 409
    junk = client.put(f"/vault/items/{case.item}/share", headers=case.owner, json={
        "ciphertext": "x", "keys": {case.ids[0]: {"wrapped_key": "AAAA", "public_key_sha256": sha(case.keys[0])}}})
    assert junk.status_code == 422
    assert client.put(f"/vault/items/{case.item}/share", headers=stranger,
                      json={"ciphertext": "x", "keys": {}}).status_code == 404
    assert client.put(f"/vault/items/{case.item}/share", json={"ciphertext": "x", "keys": {}}).status_code == 401

    done = case.publish([0])
    assert done.status_code == 200
    assert done.json() == {"delivered": [case.ids[0]], "pending": [case.ids[1]]}
    again = case.publish([0, 1], ciphertext="v1:second:blob")
    assert again.json() == {"delivered": sorted(case.ids[:2]), "pending": []}
    policy = client.get("/vault/policies", headers=case.owner).json()[0]
    assert policy["item_id"] == case.item
    assert sorted(policy["delivered_contact_ids"]) == sorted(case.ids[:2])


def test_wrapped_key_is_released_only_while_a_grant_is_active(tmp_path) -> None:
    app.state.database_path = tmp_path / "keys-release.sqlite3"
    client = TestClient(app)
    case = Case(client)
    case.register(0)
    case.confirm(0)  # contact 1 never sets up a key
    case.share_policy((0, 1))
    published = case.publish([0], ciphertext="v1:the:blob")
    assert published.json()["pending"] == [case.ids[1]]

    request_id = client.post("/access-requests", headers=case.tokens[0], json={"item_id": case.item}).json()["request_id"]
    # Before approval the contact cannot get anything from the item.
    grants_before = client.get("/contact/requests", headers=case.tokens[0]).json()["mine"][0]
    assert grants_before["grant_id"] is None

    grant_id = client.post(f"/access-requests/{request_id}/approve", headers=case.owner).json()["grant_id"]
    view = client.get(f"/access-grants/{grant_id}", headers=case.tokens[0]).json()
    assert view["share_ciphertext"] == "v1:the:blob"
    assert view["wrapped_key"]
    # The owner-encrypted ciphertext is not the share, and no raw key is ever present.
    assert set(view) >= {"share_ciphertext", "wrapped_key", "ciphertext"}

    client.post(f"/access-grants/{grant_id}/revoke", headers=case.owner)
    denied = client.get(f"/access-grants/{grant_id}", headers=case.tokens[0])
    assert denied.status_code == 403
    assert "wrapped_key" not in denied.text and "share_ciphertext" not in denied.text


def test_contact_without_a_delivered_key_gets_nulls_not_someone_elses_key(tmp_path) -> None:
    app.state.database_path = tmp_path / "keys-isolation.sqlite3"
    client = TestClient(app)
    case = Case(client)
    case.ready()
    case.publish([0])  # only contact 0 has a wrapped key

    request_id = client.post("/access-requests", headers=case.tokens[1], json={"item_id": case.item}).json()["request_id"]
    grant_id = client.post(f"/access-requests/{request_id}/approve", headers=case.owner).json()["grant_id"]
    view = client.get(f"/access-grants/{grant_id}", headers=case.tokens[1]).json()
    assert view["wrapped_key"] is None and view["share_ciphertext"] is None


def test_changing_policy_item_or_contact_invalidates_the_delivered_share(tmp_path) -> None:
    app.state.database_path = tmp_path / "keys-invalidate.sqlite3"
    client = TestClient(app)
    case = Case(client)
    case.ready()

    def delivered():
        return client.get("/vault/policies", headers=case.owner).json()[0]["delivered_contact_ids"]

    case.publish([0, 1])
    assert len(delivered()) == 2
    case.share_policy((0, 1))  # saving rules makes the owner re-publish with fresh keys
    assert delivered() == []

    case.publish([0, 1])
    client.put(f"/vault/items/{case.item}", headers=case.owner,
               json={"category": "Pets", "title": "Edited", "ciphertext": "v1:new:one"})
    assert client.get("/vault/policies", headers=case.owner).json()[0]["delivered_contact_ids"] == []

    case.publish([0, 1])
    client.delete(f"/trusted-contacts/{case.ids[1]}", headers=case.owner)
    assert client.get("/vault/policies", headers=case.owner).json()[0]["delivered_contact_ids"] == [case.ids[0]]

    client.delete(f"/vault/items/{case.item}/policy", headers=case.owner)
    assert client.get("/vault/policies", headers=case.owner).json() == []
    assert client.put(f"/vault/items/{case.item}/share", headers=case.owner,
                      json={"ciphertext": "x", "keys": {}}).status_code == 409


def test_policies_list_is_owner_scoped(tmp_path) -> None:
    app.state.database_path = tmp_path / "keys-policies.sqlite3"
    client = TestClient(app)
    case = Case(client)
    case.share_policy((0,))
    stranger = {"X-Session-Token": client.post(
        "/auth/register", json={"email": "stranger@example.com", "password": "correct horse battery"}
    ).json()["session_token"]}

    assert len(client.get("/vault/policies", headers=case.owner).json()) == 1
    assert client.get("/vault/policies", headers=stranger).json() == []
    assert client.get("/vault/policies").status_code == 401
