"""
Unit tests for rylanlabs.common collection plugins and modules.
"""

import pytest


def test_unifi_api_import() -> None:
    """Test UniFi API module imports without error."""
    from plugins.modules.unifi_api import UniFiAPI
    
    client = UniFiAPI()
    assert client is not None


def test_trinity_alignment_validation() -> None:
    """Test Trinity alignment validation utility."""
    from plugins.module_utils.rylan_utils import validate_trinity_alignment
    
    assert validate_trinity_alignment("carter-identity")
    assert validate_trinity_alignment("bauer-verify")
    assert validate_trinity_alignment("beale-harden")
    assert not validate_trinity_alignment("invalid-component")


def test_audit_log_formatting() -> None:
    """Test audit log formatting utility."""
    from plugins.module_utils.rylan_utils import format_audit_log
    
    log = format_audit_log("test_action", {"detail": "value"})
    assert log["action"] == "test_action"
    assert log["details"]["detail"] == "value"
