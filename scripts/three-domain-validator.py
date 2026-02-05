#!/usr/bin/env python3

"""3-Domain Consensus Validator (TDV) v2.0
Enforces the Trinity guardianship pattern across the collection.
"""

import argparse
import sys
from pathlib import Path
from typing import Any

# Refactored for rylanlab.unifi naming conventions
THREE_DOMAIN_GUARDIANS = {
    "identity": {"role": "roles/identity_role", "guardian": "Carter"},
    "audit": {"role": "roles/verification_role", "guardian": "Bauer"},
    "hardening": {"role": "roles/hardening_role", "guardian": "Beale"},
}

CORE_PLUGINS = [
    "plugins/modules/unifi_api.py",
    "plugins/module_utils/unifi_api.py",
    "plugins/inventory/unifi_dynamic_inventory.py"
]

class ThreeDomainValidator:
    def __init__(self, workspace: str):
        self.workspace = Path(workspace).resolve()
        self.failed: bool = False

    def log(self, status: bool, message: str) -> None:
        symbol = "✅" if status else "❌"
        print(f"{symbol} {message}")
        if not status:
            self.failed = True

    def run(self) -> bool:
        print("--- 3-Domain Consensus Validator v2.0 ---")
        
        # 1. Check Roles
        for name, config in THREE_DOMAIN_GUARDIANS.items():
            path = self.workspace / config["role"]
            is_valid = (path / "tasks" / "main.yml").exists()
            self.log(is_valid, f"[{config['guardian']}] Role Integrity: {config['role']}")

        # 2. Check Core Plugins
        for plugin in CORE_PLUGINS:
            is_valid = (self.workspace / plugin).exists()
            self.log(is_valid, f"System Plugin: {plugin}")

        return not self.failed

if __name__ == "__main__":
    validator = ThreeDomainValidator(".")
    if not validator.run():
        sys.exit(1)
    sys.exit(0)
