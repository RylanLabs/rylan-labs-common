import json

from plugins.module_utils.audit_trail_writer import write_audit_log


def test_write_audit_log_success(tmp_path):
    audit_dir = tmp_path / "audit"
    audit_dir.mkdir()

    operation = "test_op"
    target = "test_target"
    status = "SUCCESS"
    details = {"drift_count": 5, "latency_ms": 150}

    log_path = write_audit_log(audit_dir, operation, target, status, details)

    assert log_path.exists()
    assert log_path.name.startswith(f"{operation}-{target}-")
    assert log_path.name.endswith(".json")

    with open(log_path) as f:
        data = json.load(f)

    assert data["operation"] == operation
    assert data["target"] == target
    assert data["status"] == status
    assert data["guardian"] == "Bauer"
    assert data["metrics"]["drift_detected"] == 5
    assert data["metrics"]["remediation_latency_ms"] == 150


def test_write_audit_log_migration_metric(tmp_path):
    audit_dir = tmp_path / "audit"
    audit_dir.mkdir()

    log_path = write_audit_log(audit_dir, "migration", "network", "COMPLETED", {})

    with open(log_path) as f:
        data = json.load(f)

    assert data["metrics"]["complexity_reduction_pct"] == 28.0
