#!/usr/bin/env python3
"""UniFi Dynamic Inventory plugin for Ansible.

Generates dynamic inventory from UniFi controller,
enabling runtime topology discovery and device grouping.
"""

from __future__ import annotations

import os
import subprocess  # nosec: B404
import sys
from typing import Any

import yaml
from ansible.plugins.inventory import BaseInventoryPlugin

# Add module_utils to path for UnifiAPI
try:
    from ansible_collections.rylanlabs.unifi.plugins.module_utils.unifi_api import (
        UnifiAPI,
    )
except ImportError:
    try:
        from ..module_utils.unifi_api import UnifiAPI
    except (ImportError, ValueError):
        sys.path.append(os.path.join(os.path.dirname(__file__), "..", "module_utils"))
        try:
            from unifi_api import UnifiAPI
        except ImportError:
            UnifiAPI = None

DOCUMENTATION = r"""
---
name: unifi_inventory
plugin_type: inventory
short_description: RylanLabs UniFi Dynamic Hybrid Inventory
description:
    - Merges UniFi Controller API data with static device-manifest.yml
    - Supports MAC-based identity matching
options:
    plugin:
        description: plugin name (must be rylanlabs.unifi.unifi_inventory)
        required: true
        choices: ['rylanlabs.unifi.unifi_inventory']
    host:
        description: UniFi Controller Host
        type: str
    port:
        description: UniFi Controller Port
        type: int
        default: 443
    username:
        description: UniFi Controller Username
        type: str
    password:
        description: UniFi Controller Password
        type: str
    manifest_path:
        description: Path to device-manifest.yml
        type: str
        default: 'inventory/device-manifest.yml'
    vault_path:
        description: Path to encrypted unifi_vault.yml
        type: str
    vault_password_file:
        description: Path to vault password file
        type: str
"""


class InventoryModule(BaseInventoryPlugin):
    """Dynamic inventory from UniFi controller."""

    NAME = "rylanlabs.unifi.unifi_inventory"

    def __init__(self) -> None:
        """Initialize inventory module."""
        super().__init__()
        self.client: UnifiAPI | None = None

    def verify_file(self, path: str) -> bool:
        """Verify inventory file."""
        is_unifi_file = path.endswith("unifi_inventory.yml") or path.endswith(
            "unifi_inventory.yaml"
        )
        return super().verify_file(path) and is_unifi_file

    def _load_vault_secrets(
        self, vault_path: str, vault_password_file: str | None = None
    ) -> dict[str, Any]:
        """Load secrets using ansible-vault."""
        cmd = ["ansible-vault", "view", vault_path]
        if vault_password_file:
            cmd.extend(["--vault-password-file", vault_password_file])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)  # nosec: S603
            return yaml.safe_load(result.stdout)
        except (subprocess.CalledProcessError, OSError, yaml.YAMLError) as e:
            # Don't fail inventory parse on vault read errors; return empty secrets and log.
            print(f"WARN: Could not load vault secrets ({e})")
            return {}

    def parse(self, inventory: Any, loader: Any, path: str, cache: bool = True) -> None:
        """Parse inventory from UniFi controller."""
        super().parse(inventory, loader, path)

        # 1. Load config from file
        self._read_config_data(path)

        host = self.get_option("host") or os.getenv("UNIFI_HOST")
        port = int(self.get_option("port") or os.getenv("UNIFI_PORT", "443"))
        user = self.get_option("username") or os.getenv("UNIFI_USER")
        password = self.get_option("password") or os.getenv("UNIFI_PASS")
        manifest_path = self.get_option("manifest_path") or os.getenv(
            "MANIFEST_PATH", "inventory/device-manifest.yml"
        )

        # 2. Vault integration fallback
        vault_path = self.get_option("vault_path")
        if not (user and password) and vault_path and os.path.exists(vault_path):
            vault_pass_file = self.get_option("vault_password_file")
            secrets = self._load_vault_secrets(vault_path, vault_pass_file)
            user = secrets.get("unifi_api_user") or secrets.get("unifi_user")
            password = secrets.get("unifi_api_pass") or secrets.get("unifi_pass")
            host = host or secrets.get("unifi_host")

        if not UnifiAPI:
            raise Exception(
                "UnifiAPI module_util not found. Ensure collection is installed correctly."
            )

        # 3. Initialize API Client
        self.client = UnifiAPI(
            host=host, port=port, username=user, password=password, verify_ssl=False
        )

        # 4. Fetch Live Data
        live_devices = self.client.get_devices()
        live_clients = self.client.get_clients()

        # 5. Load Static Manifest
        static_manifest = {}
        if os.path.exists(manifest_path):
            with open(manifest_path) as f:
                static_manifest = yaml.safe_load(f) or {}

        # Normalize manifest (both dict and list format supported)
        devices_manifest = static_manifest.get("devices", [])
        if isinstance(devices_manifest, dict):
            devices_manifest = [{"name": k, **v} for k, v in devices_manifest.items()]

        # 6. Merge & Populate Inventory
        live_map = {d.get("mac", "").lower(): d for d in live_devices if d.get("mac")}
        client_map = {c.get("mac", "").lower(): c for c in live_clients if c.get("mac")}

        # Process manifest-defined devices (Primary Truth)
        for m_dev in devices_manifest:
            hostname = m_dev.get("name") or m_dev.get("hostname")
            mac = (m_dev.get("mac") or "").lower()
            if not hostname:
                continue

            self.inventory.add_host(hostname)

            # Map Live Info
            live_info = live_map.get(mac) or client_map.get(mac) or {}

            # Merit state: -1 (Offline), 1 (Online)
            state = 1 if live_info else -1

            # Set variables (Merge Manifest + Live)
            self.inventory.set_variable(hostname, "mac", mac)
            self.inventory.set_variable(
                hostname, "ansible_host", m_dev.get("ip") or live_info.get("ip")
            )
            self.inventory.set_variable(hostname, "live_state", state)
            self.inventory.set_variable(hostname, "unifi_managed", bool(live_info))

            # Custom Manifest Fields
            for key in ["role", "tier", "ministry", "boot_order"]:
                if key in m_dev:
                    self.inventory.set_variable(hostname, key, m_dev[key])

            # Grouping
            if "tier" in m_dev:
                tier_group = f"tier_{m_dev['tier']}"
                self.inventory.add_group(tier_group)
                self.inventory.add_child(tier_group, hostname)

            if "role" in m_dev:
                role_group = f"role_{m_dev['role']}"
                self.inventory.add_group(role_group)
                self.inventory.add_child(role_group, hostname)

        # 7. discovery of non-manifest devices
        manifest_macs = {
            (d.get("mac") or "").lower() for d in devices_manifest if d.get("mac")
        }
        for mac, l_dev in live_map.items():
            if mac not in manifest_macs:
                discover_name = l_dev.get("name") or f"unmanaged-{mac.replace(':', '')}"
                self.inventory.add_host(discover_name)
                self.inventory.add_group("undocumented")
                self.inventory.add_child("undocumented", discover_name)
                self.inventory.set_variable(
                    discover_name, "ansible_host", l_dev.get("ip")
                )
                self.inventory.set_variable(discover_name, "mac", mac)
                self.inventory.set_variable(discover_name, "unifi_managed", True)
                self.inventory.set_variable(discover_name, "in_manifest", False)
