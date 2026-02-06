"""RylanLabs Audit Logger."""
# File: plugins/module_utils/rylan_audit_logger.py
# Guardian: Bauer | Ministry: Verification & Audit
# Purpose: Seven Pillars Pillar 4 (Audit Logging) Implementation

import json
import os
import time
import subprocess
import shutil
import logging
from datetime import datetime
from typing import Optional


logger = logging.getLogger(__name__)


class RylanAuditLogger:
    """Standardizes audit logging across all RylanLabs modules.
    Writes JSON trails to the .audit/ directory and attempts best-effort GPG signatures.
    """

    def __init__(self, module_name, guardian):
        self.module_name = module_name
        self.guardian = guardian
        self.audit_dir = os.path.join(os.getcwd(), ".audit")

        if not os.path.exists(self.audit_dir):
            try:
                os.makedirs(self.audit_dir)
            except OSError:
                # Fallback to current directory if .audit cannot be created
                self.audit_dir = os.getcwd()

    def write_trail(
        self, operation, status, results=None, changed=False
    ) -> Optional[str]:
        """Writes a structured JSON audit trail and attempts to sign it.

        Returns the filepath on success, or None if writing fails.
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        filename = f"audit-{self.module_name}-{operation}-{int(time.time())}.json"
        filepath = os.path.join(self.audit_dir, filename)

        trail_data = {
            "timestamp": timestamp,
            "module": self.module_name,
            "guardian": self.guardian,
            "operation": operation,
            "status": status,
            "changed": changed,
            "results": results or {},
        }

        try:
            with open(filepath, "w") as f:
                json.dump(trail_data, f, indent=2)

            # Attempt best-effort GPG signing for tamper-evidence
            if shutil.which("gpg"):
                try:
                    subprocess.run(
                        [
                            "gpg",
                            "--armor",
                            "--detach-sign",
                            "--output",
                            f"{filepath}.asc",
                            filepath,
                        ],
                        check=True,
                    )
                    logger.debug("Signed audit trail: %s", filepath)
                except subprocess.CalledProcessError as e:
                    logger.warning("Failed to sign audit trail %s: %s", filepath, e)
            else:
                logger.debug("gpg not found; skipping audit signing for %s", filepath)

            return filepath
        except OSError as e:
            logger.error("Failed to write audit trail %s: %s", filepath, e)
            return None
