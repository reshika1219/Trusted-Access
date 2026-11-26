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


def test_logout_invalidates_the_session_server_side(tmp_path) -> None:
    from fastapi.testclient import TestClient

    from trusted_access.main import app

    app.state.database_path = tmp_path / "logout.sqlite3"
    client = TestClient(app)
    token = client.post(
        "/auth/register",
        json={"email": "logout@example.com", "password": "correct horse battery"},
    ).json()["session_token"]
    headers = {"X-Session-Token": token}
    assert client.get("/auth/me", headers=headers).status_code == 200

    assert client.post("/auth/logout", headers=headers).status_code == 200
    assert client.get("/auth/me", headers=headers).status_code == 401
    # Logging out again, or with no token at all, is harmless.
    assert client.post("/auth/logout", headers=headers).status_code == 200
    assert client.post("/auth/logout").status_code == 200


def test_repeated_failed_logins_are_throttled(tmp_path) -> None:
    from fastapi.testclient import TestClient

    from trusted_access.main import LOGIN_MAX_FAILURES, app, reset_login_throttle

    reset_login_throttle()
    app.state.database_path = tmp_path / "throttle.sqlite3"
    client = TestClient(app)
    credentials = {"email": "throttle@example.com", "password": "correct horse battery"}
    client.post("/auth/register", json=credentials)

    for _ in range(LOGIN_MAX_FAILURES):
        wrong = client.post("/auth/login", json={**credentials, "password": "not the password!"})
        assert wrong.status_code == 401
    blocked = client.post("/auth/login", json=credentials)
    assert blocked.status_code == 429
    assert "Too many failed" in blocked.json()["detail"]
    # Other accounts are unaffected.
    other = client.post("/auth/register", json={"email": "other-throttle@example.com", "password": "correct horse battery"})
    assert other.status_code == 201

    reset_login_throttle()
    assert client.post("/auth/login", json=credentials).status_code == 200


def test_successful_login_clears_earlier_failures(tmp_path) -> None:
    from fastapi.testclient import TestClient

    from trusted_access.main import LOGIN_MAX_FAILURES, app, reset_login_throttle

    reset_login_throttle()
    app.state.database_path = tmp_path / "throttle-clear.sqlite3"
    client = TestClient(app)
    credentials = {"email": "clear@example.com", "password": "correct horse battery"}
    client.post("/auth/register", json=credentials)
    for _ in range(LOGIN_MAX_FAILURES - 1):
        client.post("/auth/login", json={**credentials, "password": "not the password!"})
    assert client.post("/auth/login", json=credentials).status_code == 200
    for _ in range(LOGIN_MAX_FAILURES - 1):
        client.post("/auth/login", json={**credentials, "password": "not the password!"})
    assert client.post("/auth/login", json=credentials).status_code == 200
    reset_login_throttle()
