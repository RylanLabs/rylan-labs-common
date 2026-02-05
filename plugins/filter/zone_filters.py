"""Zone lookup filters for OON architecture.

Provides zone_by_vlan, zone_by_name, policy_by_id helpers.
"""

from typing import Any


def zone_by_vlan(zones: list[dict[str, Any]], vlan_id: int) -> dict[str, Any] | None:
    """Find zone containing specific VLAN ID."""
    for zone in zones:
        if "vlans" in zone and vlan_id in zone.get("vlans", []):
            return zone
    return None


def zone_by_name(zones: list[dict[str, Any]], zone_name: str) -> dict[str, Any] | None:
    """Find zone by name."""
    for zone in zones:
        if zone.get("name") == zone_name:
            return zone
    return None


def policy_by_id(policies: list[dict[str, Any]], policy_id: str) -> dict[str, Any] | None:
    """Find policy by ID."""
    for policy in policies:
        if policy.get("id") == policy_id:
            return policy
    return None


def flatten_oon_groups(groups: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten hierarchical OON groups into a flat list of leaf objects."""
    flat_list: list[dict[str, Any]] = []

    def walk(obj: Any, prefix: str = "") -> None:
        if not isinstance(obj, dict):
            return

        # If it has 'type' and 'members', it's a leaf group
        if "type" in obj and ("members" in obj or "protocol" in obj):
            leaf: dict[str, Any] = obj.copy()
            # If prefix exists, we might want to prepend it,
            # but usually OON names are unique identifiers
            flat_list.append(leaf)
            return

        for key, value in obj.items():
            if isinstance(value, dict):
                # If the child is a group, we might want to preserve the name
                if "name" not in value:
                    value["name"] = key
                walk(value, prefix + key + ".")

    walk(groups)
    return flat_list


class FilterModule:
    """Ansible filter module for OON architecture."""

    def filters(self) -> dict[str, Any]:
        """Return the filter mappings."""
        return {
            "zone_by_vlan": zone_by_vlan,
            "zone_by_name": zone_by_name,
            "policy_by_id": policy_by_id,
            "flatten_oon_groups": flatten_oon_groups,
        }
