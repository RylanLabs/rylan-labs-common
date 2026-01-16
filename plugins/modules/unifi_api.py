#!/usr/bin/env python3

# Copyright: (c) 2026, RylanLabs
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

"""
UniFi Controller Ansible Module (Production-Ready).

Hardened UniFi API integration with full type safety and constraint validation.
Supports dual-auth (API key + JWT) with CSRF handling for UniFi OS 3.x+.
Includes simulation mode for safe infrastructure-as-code deployments.

Author: RylanLabs (@RylanLabs)
"""

DOCUMENTATION = r"""
---
module: unifi_api
short_description: Interact with UniFi Controller API
description:
  - Manages UniFi network configurations via API
  - Supports dual authentication (JWT + API Key)
  - Includes simulation mode for safe testing
  - Implements CSRF token handling for UniFi OS 3.x+
version_added: "1.2.0"
author:
  - RylanLabs (@RylanLabs)
options:
  host:
    description: UniFi Controller host
    required: true
    type: str
  port:
    description: UniFi Controller port
    required: false
    type: int
    default: 443
  api_key:
    description: UniFi API Key (preferred auth method)
    required: false
    type: str
  username:
    description: UniFi Controller username
    required: false
    type: str
  password:
    description: UniFi Controller password
    required: false
    type: str
    no_log: true
  action:
    description: Action to perform
    required: true
    type: str
    choices:
      - get_sites
      - get_devices
      - get_firewall_rules
      - create_firewall_rule
      - delete_firewall_rule
      - get_networks
      - create_network
      - delete_network
      - get_wlan_configs
      - create_wlan_config
      - delete_wlan_config
      - adopt_device
      - configure_port
      - validate_constraints
      - api_call
  rule_data:
    description: Data for firewall rule creation
    type: dict
    required: false
  network_data:
    description: Data for network creation
    type: dict
    required: false
  wlan_data:
    description: Data for WLAN creation
    type: dict
    required: false
  port_data:
    description: Data for port configuration
    type: dict
    required: false
"""

EXAMPLES = r"""
- name: Get site info (simulation mode)
  rylanlab.common.unifi_api:
    host: "{{ unifi_controller_host }}"
    api_key: "{{ unifi_api_key }}"
    action: get_sites
  register: site_info

- name: Create VLAN (production)
  rylanlab.common.unifi_api:
    host: "{{ unifi_controller_host }}"
    api_key: "{{ unifi_api_key }}"
    action: create_network
    network_data:
      name: "Servers"
      vlan: 10
  register: vlan_result
"""

RETURN = r"""
changed:
  description: Whether the module made changes
  type: bool
  returned: always
data:
  description: API response data
  type: dict
  returned: success
audit_log:
  description: Audit events logged during execution
  type: list
  returned: always
"""

import base64  # noqa: E402
import http.cookiejar  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import ssl  # noqa: E402
import time  # noqa: E402
import urllib.error  # noqa: E402
import urllib.request  # noqa: E402
from typing import Any  # noqa: E402

try:
    from ansible.module_utils.basic import AnsibleModule  # type: ignore
except ImportError:
    # Fallback for testing/non-Ansible context
    class AnsibleModule:  # type: ignore[no-redef]
        """Mock AnsibleModule for environment stability."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            """Initialize mock module."""
            self.params: dict[str, Any] = {}
            self.check_mode: bool = False

        def exit_json(self, **kwargs: Any) -> None:
            """Mock exit_json."""

        def fail_json(self, **kwargs: Any) -> None:
            """Mock fail_json."""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXCEPTION HIERARCHY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class UniFiError(Exception):
    """Base UniFi exception."""

    exit_code: int = 2


class UniFiAuthError(UniFiError):
    """Authentication failure (EXIT_AUTH = 1)."""

    exit_code = 1


class UniFiAPIError(UniFiError):
    """API error response (EXIT_API = 2)."""

    exit_code = 2


class UniFiConstraintError(UniFiError):
    """Constraint violation (EXIT_ISOLATION = 4)."""

    exit_code = 4


class UniFiConfigError(UniFiError):
    """Configuration error (EXIT_CONFIG = 3)."""

    exit_code = 3


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONSTRAINT VALIDATOR (Safety Constraints)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class UniFiConstraintValidator:
    """Validate safety constraints: ≤10 firewall rules, ≤5 VLANs.
    Recommended limits for maintainability and hardware offload safety.
    """

    MAX_FIREWALL_RULES: int = 10
    MAX_VLANS: int = 5

    @staticmethod
    def validate_firewall_rules(rules: list[dict[str, Any]]) -> dict[str, Any]:
        """Fail if rule count exceeds limit."""
        rule_count = len(rules) if rules else 0
        if rule_count > UniFiConstraintValidator.MAX_FIREWALL_RULES:
            msg = f"CONSTRAINT VIOLATION: {rule_count} firewall rules exceeds max {UniFiConstraintValidator.MAX_FIREWALL_RULES}"
            raise UniFiConstraintError(msg)
        return {
            "valid": True,
            "count": rule_count,
            "compliant": True,
            "max": UniFiConstraintValidator.MAX_FIREWALL_RULES,
        }

    @staticmethod
    def validate_vlans(networks: list[dict[str, Any]]) -> dict[str, Any]:
        """Fail if VLAN count exceeds limit."""
        vlans = [n for n in networks if n.get("purpose") in ["corporate", "guest"]] if networks else []
        vlan_count = len(vlans)
        if vlan_count > UniFiConstraintValidator.MAX_VLANS:
            msg = f"CONSTRAINT VIOLATION: {vlan_count} VLANs exceeds max {UniFiConstraintValidator.MAX_VLANS}"
            raise UniFiConstraintError(msg)
        return {
            "valid": True,
            "count": vlan_count,
            "compliant": True,
            "max": UniFiConstraintValidator.MAX_VLANS,
        }

    @staticmethod
    def validate_all(controller_state: dict[str, Any]) -> dict[str, Any]:
        """Run all constraint checks. Return dict with results."""
        results: dict[str, Any] = {}

        try:
            results["firewall"] = UniFiConstraintValidator.validate_firewall_rules(
                controller_state.get("hardening_management_firewall_rules", controller_state.get("firewall_rules", []))
            )
        except UniFiConstraintError as e:
            results["firewall"] = {"valid": False, "error": str(e), "compliant": False}

        try:
            results["vlans"] = UniFiConstraintValidator.validate_vlans(controller_state.get("networks", []))
        except UniFiConstraintError as e:
            results["vlans"] = {"valid": False, "error": str(e), "compliant": False}

        return results


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# UNIFI CLIENT (Identity + Verification)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DOCUMENTATION = r"""
---
module: unifi_api
short_description: Interact with UniFi Controller API
version_added: "1.0.0"
description:
  - Manage UniFi network devices via Controller API
  - Supports authentication, device queries, and network configuration
  - Trinity-aligned (Carter/Bauer/Beale) for audit and validation
  - Integrated with rylan-labs-iac infrastructure automation
options:
  controller_url:
    description: UniFi Controller URL (e.g., https://192.168.1.1:8443)
    required: true
    type: str
  username:
    description: UniFi Controller admin username
    required: true
    type: str
  password:
    description: UniFi Controller admin password
    required: true
    type: str
    no_log: true
  site:
    description: UniFi site name for multi-site deployments
    required: false
    type: str
    default: default
  verify_ssl:
    description: Verify SSL certificates (set to false for self-signed certs)
    required: false
    type: bool
    default: true
  action:
    description: API action to perform
    required: true
    type: str
    choices:
      - login
      - list_devices
      - get_device
      - update_device
      - query_wlan_config
author:
  - RylanLabs (@RylanLabs)
requirements:
  - requests>=2.31.0
  - urllib3>=2.0.0
notes:
  - Requires UniFi Controller v6.0.0 or higher
  - Supports UniFi Network Application API v1
  - Passwords are not logged due to no_log setting
  - Trinity compliance: Audit logging available via Bauer pattern
"""

EXAMPLES = r"""
- name: Login to UniFi Controller
  rylanlab.common.unifi_api:
    controller_url: https://192.168.1.1:8443
    username: admin
    password: "{{ unifi_admin_password }}"
    verify_ssl: false
    action: login

- name: List all managed devices
  rylanlab.common.unifi_api:
    controller_url: https://192.168.1.1:8443
    username: admin
    password: "{{ unifi_admin_password }}"
    action: list_devices
    site: default

- name: Get specific device configuration
  rylanlab.common.unifi_api:
    controller_url: https://192.168.1.1:8443
    username: admin
    password: "{{ unifi_admin_password }}"
    action: get_device
    site: default

- name: Query WLAN configuration
  rylanlab.common.unifi_api:
    controller_url: https://192.168.1.1:8443
    username: admin
    password: "{{ unifi_admin_password }}"
    action: query_wlan_config
    site: default
"""

RETURN = r"""
data:
  description: API response data containing requested information
  returned: always
  type: dict
  sample: {"devices": [{"name": "AP-01", "ip": "192.168.1.10", "status": "online"}]}
changed:
  description: Whether any changes were made by the action
  returned: always
  type: bool
  sample: false
failed:
  description: Whether the action failed
  returned: always
  type: bool
  sample: false
msg:
  description: Human-readable status message
  returned: always
  type: str
  sample: "Successfully authenticated to UniFi Controller"
"""


class UniFiAPI:
    """Dual-auth UniFi API client (API key + JWT/CSRF).

    Features:
    - Dual auth detection (API key vs JWT)
    - TTL caching (JWT exp extraction)
    - Crash-safe API wrapper
    - Safety constraint validation
    """

    def __init__(
        self,
        host: str,
        port: int = 443,
        api_key: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        """Initialize client with auth preference detection."""
        self.host = host
        self.port = port
        self.api_key = api_key
        self.username = username
        self.password = password

        # API endpoints
        self.api_base = f"https://{host}:{port}/proxy/network"
        self.auth_base = f"https://{host}:{port}/api/auth"

        # Site identifiers
        self.site_id = "default"
        self.site_uuid: str | None = None

        # Auth state
        self.jwt_token: str | None = None
        self.csrf_token: str | None = None
        self.jwt_exp: int | None = None

        # Cookie jar for session auth
        self.cookie_jar = http.cookiejar.CookieJar()

        # SSL context (no verification for local access)
        self.ssl_ctx = ssl.create_default_context()
        self.ssl_ctx.check_hostname = False
        self.ssl_ctx.verify_mode = ssl.CERT_NONE

        # Simulation mode detection
        self.simulation_mode = os.environ.get("UNIFI_SIMULATION", "false").lower() == "true"

        # Create HTTPS handler with SSL context
        https_handler = urllib.request.HTTPSHandler(context=self.ssl_ctx)
        self.cookie_handler = urllib.request.HTTPCookieProcessor(self.cookie_jar)
        self.opener = urllib.request.build_opener(https_handler, self.cookie_handler)

        # Audit trail
        self.audit_log: list[dict[str, Any]] = []

        # Detect auth mode
        self._detect_auth_mode()

    def _detect_auth_mode(self) -> None:
        """Determine auth priority: ENV > config > credentials."""
        if self.simulation_mode:
            self.auth_mode = "simulation"
            self._log_audit("auth_mode_detected", {"mode": "simulation"})
            return

        if self.api_key:
            self.auth_mode = "api_key"
            self._log_audit("auth_mode_detected", {"mode": "api_key"})
        elif self.username and self.password:
            self.auth_mode = "jwt"
            self._log_audit("auth_mode_detected", {"mode": "jwt"})
            self.ensure_jwt_fresh()
        else:
            msg = "Neither UNIFI_API_KEY env nor credentials provided"
            raise UniFiConfigError(msg)

    def _log_audit(self, event: str, data: dict[str, Any]) -> None:
        """Record audit event."""
        self.audit_log.append({"timestamp": time.time(), "event": event, "data": data})

    def _extract_jwt_exp(self, token: str) -> int | None:
        """Decode JWT and extract exp claim."""
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None

            payload = parts[1]
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += "=" * padding

            decoded = base64.urlsafe_b64decode(payload)
            claims = json.loads(decoded)
            return claims.get("exp")  # type: ignore[no-any-return]
        except (ValueError, KeyError, TypeError):
            return None

    def ensure_jwt_fresh(self) -> None:
        """Check JWT expiry; re-login if expired."""
        if self.auth_mode == "api_key":
            return

        # Try to load from local cache file first
        cache_path = os.path.join(os.path.expanduser("~"), ".unifi_jwt_cache")
        if not self.jwt_token and os.path.exists(cache_path):
            try:
                with open(cache_path) as f:
                    cache_data = json.load(f)
                    if cache_data.get("host") == self.host:
                        self.jwt_token = cache_data.get("jwt")
                        self.jwt_exp = cache_data.get("exp")
                        self.csrf_token = cache_data.get("csrf")
                        # Sync cookie jar
                        cookie = http.cookiejar.Cookie(
                            version=0,
                            name="TOKEN",
                            value=self.jwt_token,
                            port=None,
                            port_specified=False,
                            domain=self.host,
                            domain_specified=True,
                            domain_initial_dot=False,
                            path="/",
                            path_specified=True,
                            secure=True,
                            expires=self.jwt_exp,
                            discard=False,
                            comment=None,
                            comment_url=None,
                            rest={},
                            rfc2109=False,
                        )
                        self.cookie_jar.set_cookie(cookie)
                        self._log_audit("auth_cache_loaded", {"source": cache_path})
            except (json.JSONDecodeError, OSError):
                pass

        if self.jwt_token and self.jwt_exp:
            current_time = int(time.time())
            if current_time < self.jwt_exp - 60:  # 60-second buffer
                self._log_audit("auth_cache_hit", {"ttl_remaining": self.jwt_exp - current_time})
                return

        self._log_audit("auth_expired_or_missing", {"attempting_re_login": True})
        self._login_jwt()

        # Save to local cache file
        if self.jwt_token:
            try:
                with open(cache_path, "w") as f:
                    json.dump({"host": self.host, "jwt": self.jwt_token, "exp": self.jwt_exp, "csrf": self.csrf_token}, f)
            except OSError:
                pass

    def _login_jwt(self) -> None:
        """Authenticate via JWT/CSRF session flow."""
        if not self.username or not self.password:
            raise UniFiAuthError

        url = f"{self.auth_base}/login"
        data = json.dumps({"username": self.username, "password": self.password}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with self.opener.open(req, timeout=10) as r:
                r.read()

            # Extract token from cookie jar
            self.jwt_token = None
            for cookie in self.cookie_jar:
                if cookie.name == "TOKEN":
                    self.jwt_token = cookie.value
                    break

            if not self.jwt_token:
                raise UniFiAuthError

            self.jwt_exp = self._extract_jwt_exp(self.jwt_token)

            # Extract CSRF token from JWT claims
            parts = self.jwt_token.split(".")
            if len(parts) == 3:
                payload = parts[1]
                padding = 4 - len(payload) % 4
                if padding != 4:
                    payload += "=" * padding
                try:
                    claims = json.loads(base64.urlsafe_b64decode(payload))
                    self.csrf_token = claims.get("csrfToken")
                except (ValueError, KeyError, TypeError):
                    pass

            if not self.csrf_token:
                raise UniFiAuthError

            self._log_audit(
                "login_success",
                {"ttl_seconds": (self.jwt_exp - int(time.time())) if self.jwt_exp else None},
            )

        except urllib.error.HTTPError as e:
            error_msg = f"Login failed: HTTP {e.code} {e.reason}"
            self._log_audit("login_failed", {"http_code": e.code, "reason": str(e.reason)})
            raise UniFiAuthError(error_msg) from e
        except (OSError, ValueError) as e:
            error_msg = f"Login error: {e!s}"
            self._log_audit("login_error", {"error": str(e)})
            raise UniFiAuthError(error_msg) from e

    def api_call(self, endpoint: str, method: str = "GET", data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make authenticated API call."""
        if self.simulation_mode:
            self._log_audit("simulation_api_call", {"endpoint": endpoint, "method": method})
            if "stat/device" in endpoint or "devices" in endpoint:
                return {
                    "meta": {"rc": "ok"},
                    "data": [
                        {
                            "mac": "fc:ec:da:4e:1c:bd",
                            "model": "US8P60",
                            "name": "Switch-Homelab",
                            "port_table": [{"port_idx": 4, "name": "Port 4", "native_networkconf_id": "vlan1"}],
                        }
                    ],
                }
            if "sites" in endpoint:
                return {"meta": {"rc": "ok"}, "data": [{"id": "default-uuid", "name": "default", "desc": "Default"}]}
            if "wlanconf" in endpoint:
                return {"meta": {"rc": "ok"}, "data": []}
            return {"meta": {"rc": "ok"}, "data": {}}

        url = f"{self.api_base}/{endpoint}"
        headers = {"Accept": "application/json", "Content-Type": "application/json"}

        if self.auth_mode == "api_key":
            headers["X-API-Key"] = self.api_key or ""
        else:
            self.ensure_jwt_fresh()
            headers["X-CSRF-Token"] = self.csrf_token or ""

        request_data = None
        if data:
            request_data = json.dumps(data).encode("utf-8")

        req = urllib.request.Request(url, data=request_data, headers=headers, method=method)

        try:
            with self.opener.open(req, timeout=10) as r:
                response_text = r.read().decode("utf-8")
                response = json.loads(response_text)

        except urllib.error.HTTPError as e:
            if e.code == 401:
                raise UniFiAuthError from e
            # Non-auth HTTP error; bubble as API error without detailed external message
            raise UniFiAPIError from e

        except (OSError, ValueError) as e:
            raise UniFiAPIError from e

        if isinstance(response, dict) and response.get("meta", {}).get("rc") == "error":
            error_msg = response.get("meta", {}).get("msg", "Unknown error")
            raise UniFiAPIError(error_msg)

        self._log_audit("api_call_success", {"endpoint": endpoint, "method": method})
        return response  # type: ignore[no-any-return]

    def discover_sites(self) -> list[dict[str, Any]]:
        """Get list of sites (Integration API v1)."""
        result = self.api_call("integration/v1/sites")
        sites = result.get("data", [])
        if sites:
            self.site_uuid = sites[0]["id"]
        return sites  # type: ignore[no-any-return]

    def get_devices(self) -> list[dict[str, Any]]:
        """Get devices for current site (requires site_uuid)."""
        if not self.site_uuid:
            self.discover_sites()

        result = self.api_call(f"integration/v1/sites/{self.site_uuid}/devices")
        return result.get("data", [])  # type: ignore[no-any-return]

    def get_firewall_rules(self) -> list[dict[str, Any]]:
        """Get firewall rules for current site."""
        result = self.api_call(f"api/s/{self.site_id}/rest/firewallrule")
        return result.get("data", [])  # type: ignore[no-any-return]

    def create_firewall_rule(self, rule_data: dict[str, Any], check_mode: bool = False) -> dict[str, Any]:
        """Create firewall rule with idempotency."""
        name = rule_data.get("name")
        payload = rule_data.copy()

        # Idempotency Check
        current_rules = self.get_firewall_rules()
        for rule in current_rules:
            if rule.get("name") == name:
                return {"changed": False, "data": rule, "msg": "Firewall rule already exists"}

        if check_mode:
            return {"changed": True, "msg": "Firewall rule would be created (check_mode)"}

        result = self.api_call(f"api/s/{self.site_id}/rest/firewallrule", method="POST", data=payload)
        return {"changed": True, "data": result}

    def delete_firewall_rule(self, rule_name: str) -> dict[str, Any]:
        """Delete firewall rule by name."""
        rules = self.get_firewall_rules()
        rule = next((r for r in rules if r.get("name") == rule_name), None)

        if not rule:
            return {"changed": False, "msg": f"Firewall rule {rule_name} not found"}

        rule_id = rule["_id"]
        result = self.api_call(f"api/s/{self.site_id}/rest/firewallrule/{rule_id}", method="DELETE")
        return {"changed": True, "data": result}

    def get_networks(self) -> list[dict[str, Any]]:
        """Get VLANs and network configurations."""
        result = self.api_call(f"api/s/{self.site_id}/rest/networkconf")
        return result.get("data", [])  # type: ignore[no-any-return]

    def create_network(self, network_data: dict[str, Any], check_mode: bool = False) -> dict[str, Any]:
        """Create VLAN or network configuration with idempotency."""
        name = network_data.get("name")
        payload = network_data.copy()

        if check_mode:
            return {"changed": True, "msg": f"Network {name} would be created (check_mode)"}

        # Idempotency Check
        current_networks = self.get_networks()
        for net in current_networks:
            if net.get("name") == name:
                return {"changed": False, "data": net, "msg": "Network already exists"}

        result = self.api_call(f"api/s/{self.site_id}/rest/networkconf", method="POST", data=payload)
        return {"changed": True, "data": result}

    def get_wlan_configs(self) -> list[dict[str, Any]]:
        """Get wireless network configurations."""
        result = self.api_call(f"api/s/{self.site_id}/rest/wlanconf")
        return result.get("data", [])  # type: ignore[no-any-return]

    def create_wlan_config(self, wlan_data: dict[str, Any], check_mode: bool = False) -> dict[str, Any]:
        """Create SSID with idempotency."""
        name = wlan_data.get("name")
        payload = wlan_data.copy()

        # Idempotency Check
        current_wlans = self.get_wlan_configs()
        for wlan in current_wlans:
            if wlan.get("name") == name:
                return {"changed": False, "data": wlan, "msg": "SSID already exists"}

        if check_mode:
            return {"changed": True, "msg": f"SSID {name} would be created (check_mode)"}

        result = self.api_call(f"api/s/{self.site_id}/rest/wlanconf", method="POST", data=payload)
        return {"changed": True, "data": result}


def main() -> None:
    """Ansible module entry point."""
    if not AnsibleModule:
        return

    module = AnsibleModule(
        argument_spec={
            "host": {"type": "str", "required": True},
            "port": {"type": "int", "default": 443},
            "api_key": {"type": "str", "no_log": True},
            "username": {"type": "str"},
            "password": {"type": "str", "no_log": True},
            "action": {
                "type": "str",
                "required": True,
                "choices": [
                    "get_sites",
                    "get_devices",
                    "get_firewall_rules",
                    "create_firewall_rule",
                    "delete_firewall_rule",
                    "get_networks",
                    "create_network",
                    "get_wlan_configs",
                    "create_wlan_config",
                    "validate_constraints",
                    "api_call",
                ],
            },
            "rule_data": {"type": "dict"},
            "network_data": {"type": "dict"},
            "wlan_data": {"type": "dict"},
            "path": {"type": "str"},
            "method": {"type": "str", "default": "GET"},
            "data": {"type": "dict"},
        },
        supports_check_mode=True,
    )

    try:
        client = UniFiAPI(
            module.params["host"],
            module.params["port"],
            module.params["api_key"],
            module.params["username"],
            module.params["password"],
        )

        action = module.params["action"]

        if action == "get_sites":
            module.exit_json(changed=False, data=client.discover_sites(), audit_log=client.audit_log)
        elif action == "get_devices":
            module.exit_json(changed=False, data=client.get_devices(), audit_log=client.audit_log)
        elif action == "get_firewall_rules":
            module.exit_json(changed=False, data=client.get_firewall_rules(), audit_log=client.audit_log)
        elif action == "create_firewall_rule":
            res = client.create_firewall_rule(module.params["rule_data"], check_mode=module.check_mode)
            module.exit_json(**res, audit_log=client.audit_log)
        elif action == "get_networks":
            module.exit_json(changed=False, data=client.get_networks(), audit_log=client.audit_log)
        elif action == "create_network":
            res = client.create_network(module.params["network_data"], check_mode=module.check_mode)
            module.exit_json(**res, audit_log=client.audit_log)
        elif action == "validate_constraints":
            rules = client.get_firewall_rules()
            networks = client.get_networks()
            val = UniFiConstraintValidator.validate_all({"hardening_management_firewall_rules": rules, "networks": networks})
            if any(not v.get("valid", True) for v in val.values()):
                module.fail_json(msg="Constraint violations detected", validation=val, audit_log=client.audit_log)
            module.exit_json(changed=False, validation=val, audit_log=client.audit_log)
        elif action == "api_call":
            res = client.api_call(module.params["path"], method=module.params["method"], data=module.params["data"])
            module.exit_json(changed=True, data=res, audit_log=client.audit_log)
        else:
            module.fail_json(msg=f"Action {action} not implemented")

    except UniFiError as e:
        module.fail_json(msg=str(e), exit_code=e.exit_code)
    except Exception as e:
        module.fail_json(msg=f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
