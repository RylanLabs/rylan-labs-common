#!/usr/bin/env python3

"""
3-Domain Consensus Validator (TDV) v1.0
RylanLabs Infrastructure-as-Code (IaC)

Purpose:
  Enforces the "3-Domain" guardianship pattern across the repository.
  Verifies agreement between Identity (Identity), Verification (Audit), and Hardening (Hardening).

Usage:
  python3 scripts/three-domain-validator.py --workspace .
"""

import argparse
import sys
from pathlib import Path
from typing import Any

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASES & GUARDIANS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THREE_DOMAIN_GUARDIANS = {
    "identity": {"role": "roles/identity_management", "purpose": "Identity & Auth"},
    "audit": {"role": "roles/infrastructure_verify", "purpose": "Verification & Audit"},
    "hardening": {"role": "roles/hardening_management", "purpose": "Hardening & Isolation"},
}

CORE_PLUGINS = ["plugins/modules/unifi_api.py", "plugins/module_utils/unifi_endpoints.py", "plugins/inventory/unifi_dynamic_inventory.py"]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VALIDATOR LOGIC
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class ThreeDomainValidator:
    def __init__(self, workspace: str):
        self.workspace = Path(workspace).resolve()
        self.results: list[dict[str, Any]] = []
        self.failed: bool = False

    def log(self, guardian: str, status: bool, message: str) -> None:
        symbol = "✅" if status else "❌"
        print(f"{symbol} [{guardian.upper():<8}] {message}")
        self.results.append({"guardian": guardian, "status": status, "message": message})
        if not status:
            self.failed = True

    def check_roles(self) -> None:
        print("\n--- Phase 1: 3-Domain Role Integrity ---")
        for name, config in THREE_DOMAIN_GUARDIANS.items():
            role_path = self.workspace / config["role"]
            if role_path.exists() and (role_path / "tasks" / "main.yml").exists():
                self.log(name, True, f"Guardian role exists: {config['role']}")
            else:
                self.log(name, False, f"MISSING Guardian role: {config['role']}")

    def check_plugins(self) -> None:
        print("\n--- Phase 2: Plugin Integrity ---")
        for plugin in CORE_PLUGINS:
            plugin_path = self.workspace / plugin
            if plugin_path.exists():
                self.log("system", True, f"Core plugin found: {plugin}")
            else:
                self.log("system", False, f"MISSING core plugin: {plugin}")

    def check_endpoints(self) -> None:
        print("\n--- Phase 3: Endpoint Registry Consensus ---")
        try:
            # Add workspace to path to allow import
            sys.path.append(str(self.workspace))
            from plugins.module_utils.unifi_endpoints import ENDPOINTS, RESPONSIBILITY_MAP

            coverage = len(ENDPOINTS)
            self.log("audit", True, f"Endpoint Registry Coverage: {coverage} endpoints")

            # Verify every endpoint is mapped
            unmapped = [k for k in ENDPOINTS if k not in RESPONSIBILITY_MAP]
            if not unmapped:
                self.log("audit", True, "All endpoints mapped to responsibilities")
            else:
                self.log("audit", False, f"Unmapped endpoints found: {unmapped}")
        except Exception as e:
            self.log("audit", False, f"Failed to validate endpoint consensus: {e}")

    def run(self) -> bool:
        print("======================================================")
        print("           3-DOMAIN CONSENSUS VALIDATOR v1.0          ")
        print("======================================================")

        self.check_roles()
        self.check_plugins()
        self.check_endpoints()

        print("\n======================================================")
        if self.failed:
            print("❌ CONSENSUS FAILED: Repository state inconsistent.")
            return False
        print("✅ CONSENSUS REACHED: 3-Domain Guardians aligned.")
        return True


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENTRY POINT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="3-Domain Consensus Validator")
    parser.add_argument("--workspace", default=".", help="Workspace root directory")
    args = parser.parse_args()

    validator = ThreeDomainValidator(args.workspace)
    if not validator.run():
        sys.exit(1)
    sys.exit(0)
