import shutil
import subprocess

import pytest

from trusted_access.ui import INDEX_HTML


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed")
def test_embedded_dashboard_script_is_valid_javascript(tmp_path) -> None:
    script = INDEX_HTML.split("<script>")[1].split("</script>")[0]
    path = tmp_path / "dashboard.js"
    path.write_text(script, encoding="utf-8")

    result = subprocess.run(
        ["node", "--check", str(path)], capture_output=True, text=True, check=False
    )

    assert result.returncode == 0, result.stderr


def test_dashboard_has_exactly_one_inline_script_and_no_inline_handlers() -> None:
    # The Content-Security-Policy allows one script by hash, and inline event
    # handler attributes would be blocked by it.
    assert INDEX_HTML.count("<script") == 1
    for handler in (" onclick=", " onerror=", " onload=", " onsubmit="):
        assert handler not in INDEX_HTML.split("<script>")[0]
