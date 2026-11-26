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


def test_dashboard_offers_validated_backup_restore(tmp_path) -> None:
    app.state.database_path = tmp_path / "ui.sqlite3"
    html = TestClient(app).get("/").text

    assert "Restore from a backup" in html
    assert 'type="file"' in html
    assert "function parseBackup" in html
    assert 'api("/backup/import"' in html
    assert "Sharing rules aren't included in backups" in html


def test_dashboard_encrypts_the_whole_backup_client_side(tmp_path) -> None:
    app.state.database_path = tmp_path / "ui.sqlite3"
    html = TestClient(app).get("/").text

    assert "Download encrypted backup" in html
    assert "PBKDF2" in html and "AES-256-GCM" in html
    assert "additionalData: BACKUP_AAD" in html
    assert "KDF.min" in html and "KDF.max" in html
    assert "Unlock backup" in html
    # The old plaintext download and preview must be gone.
    assert 'id="preview"' not in html
    assert "JSON.stringify(backupData" not in html


def test_dashboard_supports_editing_deleting_and_server_logout(tmp_path) -> None:
    app.state.database_path = tmp_path / "ui.sqlite3"
    html = TestClient(app).get("/").text

    assert 'id="edit-dialog"' in html
    assert "data-del-item" in html and "data-del-contact" in html
    assert 'api("/auth/logout"' in html


def test_dashboard_includes_the_trusted_contact_portal(tmp_path) -> None:
    app.state.database_path = tmp_path / "ui.sqlite3"
    html = TestClient(app).get("/").text

    assert "I'm a trusted contact" in html
    assert 'id="portal"' in html and "Waiting for your approval" in html
    assert 'api("/contact/requests"' in html and "contact-approve" in html
    # Invite links carry the token in the URL fragment, which is never sent to the server.
    assert "#contact=" in html
    # Viewing a grant must not create an encryption key as a side effect.
    assert "encryptionKey(false)" in html


def test_csp_allows_only_the_pages_own_script_by_hash(tmp_path) -> None:
    import base64
    import hashlib
    import re

    app.state.database_path = tmp_path / "ui.sqlite3"
    response = TestClient(app).get("/")
    csp = response.headers["content-security-policy"]

    script = re.findall(r"<script>(.*?)</script>", response.text, flags=re.S)
    assert len(script) == 1
    digest = base64.b64encode(hashlib.sha256(script[0].encode()).digest()).decode()
    assert f"script-src 'sha256-{digest}'" in csp
    assert "default-src 'none'" in csp
    assert "frame-ancestors 'none'" in csp
    assert "connect-src 'self'" in csp
    assert "script-src 'unsafe-inline'" not in csp and "unsafe-eval" not in csp
    assert "camera=()" in response.headers["permissions-policy"]
    assert response.headers["cache-control"] == "no-store"


def test_api_responses_are_not_cacheable(tmp_path) -> None:
    app.state.database_path = tmp_path / "ui.sqlite3"
    response = TestClient(app).get("/health")

    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"


def test_sharing_dialog_prefills_rules_and_can_stop_sharing(tmp_path) -> None:
    app.state.database_path = tmp_path / "ui.sqlite3"
    html = TestClient(app).get("/").text

    assert 'id="policy-stop"' in html and "Stop sharing" in html
    assert '"/policy"))).policy' in html
    assert "access_policy_removed" in html


def test_dashboard_delivers_keys_with_fingerprint_confirmation(tmp_path) -> None:
    app.state.database_path = tmp_path / "ui.sqlite3"
    html = TestClient(app).get("/").text

    assert 'id="key-dialog"' in html and "The fingerprint matches" in html
    assert "async function publishShare" in html and "syncShares" in html
    assert 'name: "RSA-OAEP"' in html and "wrapKey" in html
    # The per-share key is random and fresh for every publish.
    assert 'generateKey({ name: "AES-GCM", length: 256 }, true, ["encrypt"])' in html
    # Delivery only to contacts the owner confirmed.
    assert "c.key_confirmed" in html
