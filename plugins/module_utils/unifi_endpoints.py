# Copyright: (c) 2026, RylanLabs
# GNU General Public License v3.0+

"""
UniFi API Endpoint Registry

Centralized mapping of UniFi Controller API endpoints to functional responsibilities.

Responsibility Mapping:
- Identity: Device adoption, SSH keys, bootstrap
- Audit: Backup, logs, state verification
- Hardening: Firewall rules, VLAN isolation, port configs

Endpoint Coverage: 9/15 (60%)
Field Documentation: 168+ fields
Target: 237+ fields (100% coverage)

Version: 1.0.0
Last Updated: 2026-01-14
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Canonical Endpoint Mapping (v1.0.1 Expansion)
ENDPOINTS = {
    "sites": {"path": "/api/s/", "methods": ["GET"]},
    "wlans": {"path": "/api/s/{{ site }}/rest/wlanconf", "methods": ["GET", "POST"]},
    "networks": {"path": "/api/s/{{ site }}/rest/networkconf", "methods": ["GET", "POST"]},
    "firewall": {"path": "/api/s/{{ site }}/rest/firewallrule", "methods": ["GET", "POST"]},
    "adoption": {"path": "/api/s/{{ site }}/cmd/devmgr", "methods": ["POST"]},
    "backup": {"path": "/api/s/{{ site }}/rest/setting/autobackup", "methods": ["GET"]},
    "system": {"path": "/api/s/{{ site }}/rest/setting/mgmt", "methods": ["GET"]},
    "update": {"path": "/api/s/{{ site }}/rest/setting/update", "methods": ["GET"]},
    "security": {"path": "/api/s/{{ site }}/rest/setting/connectivity", "methods": ["GET"]},
    "ports": {
        "path": "/api/s/{{ site }}/rest/portconf",  # Port profiles
        "device_ports": "/api/s/{{ site }}/stat/device/{mac}",  # Per-device ports
        "methods": ["GET", "PUT"],
        "guardian": "Hardening",
        "fields": 45,  # Estimated
    },
    "devices": {
        "path": "/api/s/{{ site }}/stat/device",
        "adopt": "/api/s/{{ site }}/cmd/devmgr",
        "methods": ["GET", "POST"],
        "guardian": "Identity",
        "fields": 78,  # Critical for DR
    },
    "clients": {
        "path": "/api/s/{{ site }}/stat/sta",
        "active": "/api/s/{{ site }}/stat/sta?within=86400",
        "methods": ["GET"],
        "guardian": "Audit",
        "fields": 52,
    },
    "radios": {
        "path": "/api/s/{{ site }}/rest/radiusprofile",  # If 802.1X related
        "device_radios": "/api/s/{{ site }}/stat/device/{mac}",  # Radio stats
        "methods": ["GET", "PUT"],
        "guardian": "Hardening",
        "fields": 34,
    },
}

# Responsibility Mapping (Consensus Source of Truth)
RESPONSIBILITY_MAP = {
    "sites": "system",
    "wlans": "identity",
    "networks": "hardening",
    "firewall": "hardening",
    "adoption": "identity",
    "backup": "audit",
    "system": "audit",
    "update": "audit",
    "security": "hardening",
    "ports": "hardening",
    "devices": "identity",
    "clients": "audit",
    "radios": "hardening",
}


class UniFiEndpointMapper:
    """Maps and manages UniFi API endpoints."""

    def __init__(self, controller_url: str, api_key: str | None = None):
        """Initialize UniFi endpoint mapper.

        Args:
            controller_url: UniFi Cloudkey Gen2 controller URL
            api_key: Optional API key for authentication
        """
        self.controller_url = controller_url
        self.api_key = api_key
        self.endpoints: dict[str, str] = {}

    def register_endpoint(self, name: str, path: str) -> None:
        """Register a new API endpoint.

        Args:
            name: Endpoint name
            path: API path relative to controller URL
        """
        self.endpoints[name] = path
        logger.info(f"Registered endpoint: {name} -> {path}")

    def get_endpoint(self, name: str) -> str | None:
        """Get full URL for named endpoint.

        Args:
            name: Endpoint name

        Returns:
            Full endpoint URL or None if not found
        """
        if name not in self.endpoints:
            logger.warning(f"Endpoint not found: {name}")
            return None

        path = self.endpoints[name]
        return f"{self.controller_url}{path}"

    def list_endpoints(self) -> dict[str, str]:
        """List all registered endpoints.

        Returns:
            Dictionary of endpoint names and paths
        """
        return self.endpoints.copy()

    @staticmethod
    def get_canonical_endpoints() -> dict[str, dict[str, Any]]:
        """Return canonical UniFi OS API endpoints (reference only).

        These endpoints are hard-coded in plugins/modules/unifi_api.py.
        This method serves as documentation for developers.

        Returns:
            Dictionary mapping operation to endpoint details
        """
        return {
            # Discovery & Querying
            "discover_sites": {
                "endpoint": "integration/v1/sites",
                "method": "GET",
                "description": "Discover all sites in controller",
            },
            "get_devices": {
                "endpoint": "integration/v1/sites/{site_id}/devices",
                "method": "GET",
                "description": "Get devices (APs, switches, USG) for site",
            },
            # Firewall Rules (Hardening Enforcement)
            "get_firewall_rules": {
                "endpoint": "api/s/{{ site }}/rest/firewallrule",
                "method": "GET",
                "description": "Fetch firewall rules (Production Standards constraint: max 10)",
            },
            "create_firewall_rule": {
                "endpoint": "api/s/{{ site }}/rest/firewallrule",
                "method": "POST",
                "description": "Create firewall rule (requires Hardening validation)",
            },
            # VLANs / Network Configuration (Hardening Enforcement)
            "get_networks": {
                "endpoint": "api/s/{{ site }}/rest/networkconf",
                "method": "GET",
                "description": "Fetch VLANs and network configs (Production Standards constraint: max 5)",
            },
            "create_network": {
                "endpoint": "api/s/{{ site }}/rest/networkconf",
                "method": "POST",
                "description": "Create VLAN (requires Hardening validation)",
            },
            # Wireless Configuration (Identity Pattern)
            "get_wlan_configs": {
                "endpoint": "api/s/{{ site }}/rest/wlanconf",
                "method": "GET",
                "description": "Fetch wireless network configurations (Max 4 SSIDs)",
            },
            "create_wlan_config": {
                "endpoint": "api/s/{{ site }}/rest/wlanconf",
                "method": "POST",
                "description": "Create new SSID (requires Identity validation)",
            },
            # Device Management (Audit Pattern)
            "adopt_device": {
                "endpoint": "api/s/{{ site }}/cmd/devmgr",
                "method": "POST",
                "description": "Adopt unadopted device by MAC address",
            },
            # Lifecycle & Settings (Audit Audit)
            "get_backup_settings": {
                "endpoint": "api/s/{{ site }}/rest/setting/autobackup",
                "method": "GET",
                "description": "Fetch autobackup settings",
            },
            "get_console_settings": {
                "endpoint": "api/s/{{ site }}/rest/setting/super_mgmt",
                "method": "GET",
                "description": "Fetch console and management settings",
            },
            "get_system_settings": {
                "endpoint": "api/s/{{ site }}/rest/setting/mgmt",
                "method": "GET",
                "description": "Fetch general system management settings (SSH, MDNS)",
            },
            "get_update_settings": {
                "endpoint": "api/s/{{ site }}/rest/setting/update",
                "method": "GET",
                "description": "Fetch firmware update settings",
            },
            "get_wifi_global_settings": {
                "endpoint": "api/s/{{ site }}/rest/setting/wireless",
                "method": "GET",
                "description": "Fetch global WiFi performance settings",
            },
            "get_security_settings": {
                "endpoint": "api/s/{{ site }}/rest/setting/connectivity",
                "method": "GET",
                "description": "Fetch global security and connectivity settings",
            },
            # Port Management (Hardening Guard - Hardening)
            "get_port_profiles": {
                "endpoint": "api/s/{{ site }}/rest/portconf",
                "method": "GET",
                "description": "Fetch switch port profiles (VLAN assignments, PoE)",
            },
            "get_device_ports": {
                "endpoint": "api/s/{{ site }}/stat/device",
                "method": "GET",
                "description": "Fetch device-specific port status and configurations",
            },
        }
