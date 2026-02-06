"""UniFi 9.4+ OON API Adapter (Hybrid Legacy/V2 Support).

Handles tripartite dependency pattern: IP/Port groups (Legacy) -> MAC groups (V2) -> Policies (V2).
Implements Leo Section 29 discoveries (ID mapping, schedule enforcement, ap_group_ids).
"""

import logging
from typing import Any, Literal


class UniFiAPIAdapter:
    """Adapter for UniFi 9.4+ OON API quirks and version differences."""

    def __init__(self, client: Any, version: str = "9.4"):
        self.client = client
        self.version = version
        self.logger = logging.getLogger(__name__)
        self._id_cache: dict[str, str] = {}

    def create_group(
        self, group_type: Literal["ip", "port", "mac"], name: str, members: list[str]
    ) -> dict[str, Any]:
        """Create group using appropriate API endpoint based on type."""
        if group_type in ["ip", "port"]:
            # Legacy REST endpoint (Leo Section 20)
            payload = {
                "name": name,
                "group_type": "address-group" if group_type == "ip" else "port-group",
                "group_members": members,
            }
            # Note: client.post should handle the base_url + /rest/firewallgroup
            response = self.client.post("/rest/firewallgroup", payload)

            # Extract both IDs for compatibility (Leo Section 29)
            return {
                "id": response.get("external_id"),  # Use UUID for policies
                "legacy_id": response.get("_id"),  # MongoDB ID (reference only)
                "name": name,
                "type": group_type,
            }

        elif group_type == "mac":
            # V2 API endpoint (Leo Section 20)
            payload = {"name": name, "type": "CLIENTS", "members": members}
            response = self.client.post("/api/v2/network-members-group", payload)
            return {
                "id": response.get("id"),  # V2 uses UUID only
                "name": name,
                "type": group_type,
            }

        raise ValueError(f"Unknown group type: {group_type}")

    def create_policy(
        self,
        policy_type: Literal["secure", "route", "qos"],
        name: str,
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """Create policy with mandatory fields injected (Leo Section 29)."""
        # Inject mandatory schedule field (9.4+ requirement)
        if "schedule" not in config:
            config["schedule"] = {"mode": "always"}

        # Normalize action field
        if "action" in config:
            config["action"] = config["action"].upper()

        # Map policy type to endpoint
        endpoints = {
            "secure": "/api/v2/firewall-policies",
            "route": "/api/v2/routing-policies",
            "qos": "/api/v2/qos-policies",
        }

        endpoint = endpoints.get(policy_type)
        if not endpoint:
            raise ValueError(f"Unknown policy type: {policy_type}")

        payload = {"name": name, **config}
        return self.client.post(endpoint, payload)

    def normalize_wireless_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """Normalize wireless config (Leo Section 29: x_passphrase, ap_group_ids)."""
        normalized = config.copy()

        # Rename passphrase field for OS 5.0+
        if "passphrase" in normalized:
            normalized["x_passphrase"] = normalized.pop("passphrase")

        # Inject AP group requirement if missing
        if "ap_group_ids" not in normalized:
            # This would require a lookup in a real implementation
            pass

        return normalized
