"""UniFi Dynamic Inventory Plugin."""
#!/usr/bin/env python3
# File: plugins/inventory/unifi_dynamic_inventory.py
# Guardian: Carter | Ministry: Identity & Intelligence
# Purpose: Dynamic topology discovery from UniFi Controller

DOCUMENTATION = r"""
---
name: unifi_dynamic_inventory
plugin_type: inventory
short_description: UniFi Controller Dynamic Inventory
description:
  - Queries UniFi Controller for devices and builds an Ansible inventory.
options:
  plugin:
    description: Name of the plugin.
    required: true
    choices: ['rylanlab.common.unifi_dynamic_inventory', 'unifi_dynamic_inventory']
  unifi_host:
    description: UniFi controller hostname or IP.
    env:
      - name: UNIFI_HOST
    required: true
  unifi_username:
    description: UniFi controller username.
    env:
      - name: UNIFI_USER
  unifi_password:
    description: UniFi controller password.
    env:
      - name: UNIFI_PASSWORD
  unifi_api_key:
    description: UniFi API key (alternative to username/password).
    env:
      - name: UNIFI_API_KEY
  site:
    description: Site name.
    default: default
"""

from ansible.plugins.inventory import BaseInventoryPlugin, Cacheable, Constructable


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):
    NAME = "rylanlab.common.unifi_dynamic_inventory"

    def verify_file(self, path):
        """Validates the inventory configuration file."""
        return super().verify_file(path) or path.endswith(("unifi.yml", "unifi.yaml", "unifi_inventory.yml", "unifi_inventory.yaml"))

    def parse(self, inventory, loader, path, cache=True):
        super().parse(inventory, loader, path)
        self._read_config_data(path)

        # In a real implementation, this would fetch devices from /api/s/{site}/stat/device
        # For the template, we show the structure

        site_name = self.get_option("site")
        self.inventory.add_group("unifi_devices")
        self.inventory.add_group(f"site_{site_name}")

        # Simulated device discovery
        devices = [
            {"name": "usw-core-01", "ip": "10.0.1.2", "mac": "00:11:22:33:44:55", "model": "USW-Pro-24"},
            {"name": "uap-office-01", "ip": "10.0.1.10", "mac": "00:11:22:33:44:66", "model": "U6-Pro"},
        ]

        for device in devices:
            hostname = device["name"]
            self.inventory.add_host(hostname, group="unifi_devices")
            self.inventory.add_host(hostname, group=f"site_{site_name}")
            self.inventory.set_variable(hostname, "ansible_host", device["ip"])
            self.inventory.set_variable(hostname, "mac", device["mac"])
            self.inventory.set_variable(hostname, "model", device["model"])
            self.inventory.set_variable(hostname, "unifi_site", site_name)  # Multi-site tagging


def main():
    """Main entry point for testing."""
    pass


if __name__ == "__main__":
    main()
