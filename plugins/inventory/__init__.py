"""
Inventory plugins for rylanlabs.common collection.

Phase 1 (v1.0): Bootstrap inventory plugin framework.
Phase B3: Full UniFi dynamic inventory implementation.
"""

from __future__ import annotations

from plugins.inventory.unifi_dynamic_inventory import InventoryModule

__all__ = ["InventoryModule", "unifi_dynamic_inventory"]
