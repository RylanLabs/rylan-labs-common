"""Unit tests for UniFi API Adapter."""

import unittest
from unittest.mock import MagicMock

from plugins.module_utils.unifi_client import UniFiAPIAdapter


class TestUniFiAPIAdapter(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.adapter = UniFiAPIAdapter(self.mock_client)

    def test_create_group_ip(self):
        self.mock_client.post.return_value = {"external_id": "uuid-123", "_id": "mongo-123"}
        result = self.adapter.create_group("ip", "test_ips", ["1.1.1.1"])

        self.mock_client.post.assert_called_with(
            "/rest/firewallgroup", {"name": "test_ips", "group_type": "address-group", "group_members": ["1.1.1.1"]}
        )
        self.assertEqual(result["id"], "uuid-123")

    def test_create_group_mac(self):
        self.mock_client.post.return_value = {"id": "uuid-456"}
        result = self.adapter.create_group("mac", "test_macs", ["aa:bb:cc:dd:ee:ff"])

        self.mock_client.post.assert_called_with(
            "/api/v2/network-members-group", {"name": "test_macs", "type": "CLIENTS", "members": ["aa:bb:cc:dd:ee:ff"]}
        )
        self.assertEqual(result["id"], "uuid-456")

    def test_create_policy_secure_injects_schedule(self):
        self.mock_client.post.return_value = {"id": "policy-123"}
        config = {"action": "deny", "source": {"network_members_group_id": "uuid-456"}}
        self.adapter.create_policy("secure", "test_policy", config)

        # Check if schedule was injected
        call_args = self.mock_client.post.call_args[0][1]
        self.assertEqual(call_args["schedule"]["mode"], "always")
        self.assertEqual(call_args["action"], "DENY")


    def test_create_group_invalid(self):
        with self.assertRaises(ValueError):
            self.adapter.create_group("invalid", "name", [])

    def test_create_policy_invalid(self):
        with self.assertRaises(ValueError):
            self.adapter.create_policy("invalid", "name", {})

    def test_normalize_wireless_config(self):
        config = {"passphrase": "secret", "name": "SSID"}
        normalized = self.adapter.normalize_wireless_config(config)
        self.assertEqual(normalized["x_passphrase"], "secret")
        self.assertNotIn("passphrase", normalized)


if __name__ == "__main__":
    unittest.main()
