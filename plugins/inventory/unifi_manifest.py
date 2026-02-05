import os

import yaml
from ansible.plugins.inventory import BaseInventoryPlugin

DOCUMENTATION = r"""
    name: unifi_manifest
    plugin_type: inventory
    short_description: RylanLabs UniFi Device Manifest Inventory
    description:
        - Reads device-manifest.yml and populates Ansible inventory
        - Aligns with Carter Identity pattern for UniFi-gnostic objects
    options:
        plugin:
            description: plugin name (must be unifi_manifest)
            required: true
            choices: ['unifi_manifest']
        manifest_path:
            description: Path to device-manifest.yml
            default: 'inventory/device-manifest.yml'
"""


class InventoryModule(BaseInventoryPlugin):
    NAME = "rylanlab.unifi.unifi_manifest"

    def verify_file(self, path):
        return super().verify_file(path)

    def parse(self, inventory, loader, path, cache=True):
        super().parse(inventory, loader, path)

        manifest_path = self.get_option("manifest_path")
        if not os.path.exists(manifest_path):
            # Fallback for workspace structure
            manifest_path = os.path.join(os.getcwd(), manifest_path)

        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)

        # Process devices from manifest (Fixed for list structure)
        devices = manifest.get("devices", [])
        if isinstance(devices, list):
            for device in devices:
                hostname = device.get("name")
                if not hostname:
                    continue
                self.inventory.add_host(hostname)
                self.inventory.set_variable(hostname, "ansible_host", device.get("ip"))
                self.inventory.set_variable(hostname, "role", device.get("role"))
                self.inventory.set_variable(hostname, "tier", device.get("tier"))
                self.inventory.set_variable(hostname, "mac", device.get("mac"))

                # Grouping by role
                group = device.get("role", "ungrouped")
                self.inventory.add_group(group)
                self.inventory.add_child(group, hostname)
        elif isinstance(devices, dict):
            for hostname, details in devices.items():
                self.inventory.add_host(hostname)
                self.inventory.set_variable(hostname, "ansible_host", details.get("ip"))
                self.inventory.set_variable(hostname, "role", details.get("role"))
                self.inventory.set_variable(hostname, "tier", details.get("tier"))
                self.inventory.set_variable(hostname, "mac", details.get("mac"))
                group = details.get("role", "ungrouped")
                self.inventory.add_group(group)
                self.inventory.add_child(group, hostname)
            self.inventory.add_group(group)
            self.inventory.add_child(group, hostname)

            # Grouping by tier
            tier_group = "tier_{}".format(details.get("tier", "unknown"))
            self.inventory.add_group(tier_group)
            self.inventory.add_child(tier_group, hostname)
