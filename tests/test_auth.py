from fastapi.testclient import TestClient

from trusted_access.main import app


def test_register_login_and_current_user(tmp_path) -> None:
    app.state.database_path = tmp_path / "auth.sqlite3"
    client = TestClient(app)

    registered = client.post(
        "/auth/register",
        json={"email": "Owner@Example.com", "password": "correct horse battery"},
    )
    assert registered.status_code == 201
    registration = registered.json()
    assert registration["session_token"]

    current = client.get(
        "/auth/me", headers={"X-Session-Token": registration["session_token"]}
    )
    assert current.status_code == 200
    assert current.json()["email"] == "owner@example.com"

    login = client.post(
        "/auth/login",
        json={"email": "owner@example.com", "password": "correct horse battery"},
    )
    assert login.status_code == 200
    assert login.json()["session_token"]


def test_auth_rejects_short_or_wrong_password(tmp_path) -> None:
    app.state.database_path = tmp_path / "auth.sqlite3"
    client = TestClient(app)

    assert client.post(
        "/auth/register", json={"email": "owner@example.com", "password": "short"}
    ).status_code == 422
    client.post(
        "/auth/register",
        json={"email": "owner@example.com", "password": "correct horse battery"},
    )
    assert client.post(
        "/auth/login",
        json={"email": "owner@example.com", "password": "wrong password here"},
    ).status_code == 401
