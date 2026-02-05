#!/usr/bin/env python3
"""RylanLabs utilities for Ansible plugins and modules.

Shared helper functions for organization-specific logic,
maintaining DRY principles across collection.

Phase: rylan-labs-common v1.0.0 bootstrap
"""

from __future__ import annotations

from typing import Any


def format_audit_log(action: str, details: dict[str, Any]) -> dict[str, Any]:
    """Format audit log entry for structured logging."""
    return {"action": action, "details": details}


def validate_three_domain_alignment(
    component: str,
) -> bool:
    """Validate 3-Domain (Carter/Bauer/Beale) alignment."""
    valid_components = {
        "carter-identity",
        "bauer-verify",
        "beale-harden",
        "identity_management",
        "verification_audit",
        "infrastructure_fortification",
        "adversarial_simulation",
        "infrastructure_verify",
        "hardening_management",
    }
    # Handle both hyphenated and underscored versions for transition
    normalized = component.replace("-", "_")
    return normalized in {v.replace("-", "_") for v in valid_components}


def build_rollback_handler(
    action: str,
) -> dict[str, Any]:
    """Build rollback handler for error recovery."""
    return {"action": action, "handler": f"rollback_{action}"}
