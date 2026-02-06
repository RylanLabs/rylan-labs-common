import json
import os

from plugins.module_utils.rylan_audit_logger import RylanAuditLogger


def test_audit_logger_init(tmp_path):
    # Change working directory to a temp path for the test
    os.chdir(tmp_path)
    logger = RylanAuditLogger("identity_mgr", "Carter")
    assert logger.module_name == "identity_mgr"
    assert logger.guardian == "Carter"
    assert os.path.exists(os.path.join(tmp_path, ".audit"))


def test_audit_logger_write_trail(tmp_path):
    os.chdir(tmp_path)
    logger = RylanAuditLogger("identity_mgr", "Carter")

    filepath = logger.write_trail(
        "rotate_keys", "SUCCESS", {"id": "key_1"}, changed=True
    )

    assert filepath is not None
    assert os.path.exists(filepath)

    with open(filepath) as f:
        data = json.load(f)
        assert data["module"] == "identity_mgr"
        assert data["guardian"] == "Carter"
        assert data["operation"] == "rotate_keys"
        assert data["status"] == "SUCCESS"
        assert data["changed"] is True
        assert data["results"]["id"] == "key_1"


def test_audit_logger_fallback_to_cwd(tmp_path, monkeypatch):
    # Simulate directory creation failure
    os.chdir(tmp_path)

    def mock_makedirs(path):
        raise OSError("Permission Denied")

    monkeypatch.setattr(os, "makedirs", mock_makedirs)

    # We need to re-import or handle the fact that __init__ calls makedirs
    logger = RylanAuditLogger("fail_logger", "Bauer")
    assert logger.audit_dir == str(tmp_path)


def test_audit_logger_write_fail(tmp_path, monkeypatch):
    os.chdir(tmp_path)
    logger = RylanAuditLogger("fail_logger", "Bauer")

    # Mock open to fail
    def mock_open(*args, **kwargs):
        raise OSError("Write Error")

    monkeypatch.setattr("builtins.open", mock_open)

    filepath = logger.write_trail("broken", "ERROR")
    assert filepath is None
