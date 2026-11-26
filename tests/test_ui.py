from fastapi.testclient import TestClient

from trusted_access.main import app


def test_root_serves_family_friendly_dashboard(tmp_path) -> None:
    app.state.database_path = tmp_path / "ui.sqlite3"
    response = TestClient(app).get("/")

    assert response.status_code == 200
    assert "Owner dashboard" in response.text
    assert "Encrypt and save" in response.text
    assert "Prototype only" in response.text


def test_dashboard_escapes_user_content_and_sets_security_headers(tmp_path) -> None:
    app.state.database_path = tmp_path / "ui.sqlite3"
    response = TestClient(app).get("/")

    assert "const esc =" in response.text
    assert "${i.title}" not in response.text
    assert "${c.name}" not in response.text
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"


def test_dashboard_is_accessible_and_responsive(tmp_path) -> None:
    app.state.database_path = tmp_path / "ui.sqlite3"
    html = TestClient(app).get("/").text

    assert '<html lang="en">' in html
    assert 'name="viewport"' in html
    assert 'role="tablist"' in html
    assert "prefers-color-scheme: dark" in html
    assert "prefers-reduced-motion" in html


def test_dashboard_offers_demo_login_without_builtin_credentials(tmp_path) -> None:
    app.state.database_path = tmp_path / "ui.sqlite3"
    html = TestClient(app).get("/").text

    assert 'id="demo"' in html
    assert "Try the demo" in html
    assert "crypto.getRandomValues" in html
    assert "@demo.example" in html


def test_dashboard_offers_revoke_access_for_active_grants(tmp_path) -> None:
    app.state.database_path = tmp_path / "ui.sqlite3"
    html = TestClient(app).get("/").text

    assert "Revoke access" in html
    assert 'api("/access-grants")' in html
    assert '"/access-grants/" + d.revoke + "/revoke"' in html
