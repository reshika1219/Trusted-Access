from fastapi.testclient import TestClient

from trusted_access.main import app


def test_root_serves_family_friendly_dashboard(tmp_path) -> None:
    app.state.database_path = tmp_path / "ui.sqlite3"
    response = TestClient(app).get("/")

    assert response.status_code == 200
    assert "Owner dashboard" in response.text
    assert "Encrypt and save" in response.text
    assert "Prototype only" in response.text
