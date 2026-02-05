#!/usr/bin/env python3
"""UniFi Controller Ansible Module (Production-Ready).

Ported from rylan-labs-iac with full type safety and constraint validation.
Supports dual-auth (API key + JWT) with TTL caching.

Status: v2.0-eternal | Maturity: 9.5
Patterns: Carter (identity) + Bauer (verification) + Beale (constraints)
Date: 2026-01-12
"""

from __future__ import annotations

import base64
import http.cookiejar
import json
import os
import ssl
import subprocess
import time
import urllib.error
import urllib.request
from typing import Any, ClassVar, cast

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
            pass

        def fail_json(self, **kwargs: Any) -> None:
            """Mock fail_json."""
            pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXCEPTION HIERARCHY (Beale Exit Code Pattern)
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
    """Constraint violation (EXIT_ISOLATION = 4, Hellodeolu v6)."""

    exit_code = 4


class UniFiConfigError(UniFiError):
    """Configuration error (EXIT_CONFIG = 3)."""

    exit_code = 3


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONSTRAINT VALIDATOR (Beale Hardening — Hellodeolu v6)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class UniFiConstraintValidator:
    """Validate Hellodeolu v7 constraints: Dynamic limits read from config."""

    @staticmethod
    def get_limits() -> dict[str, Any]:
        """Load limits from .validation-config.yml."""
        config_path = os.path.join(os.getcwd(), ".validation-config.yml")
        if os.path.exists(config_path):
            try:
                import yaml

                with open(config_path) as f:
                    config = yaml.safe_load(f)
                    if isinstance(config, dict):
                        limits: dict[str, Any] = config.get("hardware", {}).get("capabilities", {})
                        return limits
            except (OSError, RuntimeError, ValueError):
                pass

        # Fallback to legacy limits if config missing
        return {"firewall_rules": "unlimited", "vlans": 10}

    @staticmethod
    def validate_firewall_rules(rules: list[dict[str, Any]]) -> dict[str, Any]:
        """Fail if rule count exceeds limit (if limit exists)."""
        limits = UniFiConstraintValidator.get_limits()
        max_rules = limits.get("firewall_rules")
        rule_count = len(rules) if rules else 0

        if max_rules is not None and max_rules != "unlimited":
            if rule_count > int(max_rules):
                msg = f"CONSTRAINT VIOLATION: {rule_count} firewall rules exceeds max {max_rules}"
                raise UniFiConstraintError(msg)

        return {
            "valid": True,
            "count": rule_count,
            "compliant": True,
            "max": max_rules,
        }

    @staticmethod
    def validate_vlans(networks: list[dict[str, Any]]) -> dict[str, Any]:
        """Fail if VLAN count exceeds limit (if limit exists)."""
        limits = UniFiConstraintValidator.get_limits()
        max_vlans = limits.get("vlans")
        vlans = [n for n in networks if n.get("purpose") in ["corporate", "guest"]] if networks else []
        vlan_count = len(vlans)

        if max_vlans is not None and max_vlans != "unlimited":
            if vlan_count > int(max_vlans):
                msg = f"CONSTRAINT VIOLATION: {vlan_count} VLANs exceeds max {max_vlans}"
                raise UniFiConstraintError(msg)

        return {
            "valid": True,
            "count": vlan_count,
            "compliant": True,
            "max": max_vlans,
        }

    @staticmethod
    def validate_all(controller_state: dict[str, Any]) -> dict[str, Any]:
        """Run all constraint checks. Return dict with results."""
        results: dict[str, Any] = {}

        try:
            results["firewall"] = UniFiConstraintValidator.validate_firewall_rules(
                controller_state.get("firewall_rules", [])
            )
        except UniFiConstraintError as e:
            results["firewall"] = {"valid": False, "error": str(e), "compliant": False}

        try:
            results["vlans"] = UniFiConstraintValidator.validate_vlans(controller_state.get("networks", []))
        except UniFiConstraintError as e:
            results["vlans"] = {"valid": False, "error": str(e), "compliant": False}

        return results


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# UNIFI CLIENT (Carter Identity + Bauer Verification)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class UniFiClient:
    """Dual-auth UniFi API client (API key + JWT/CSRF).

    Patterns:
    - Pattern 1 (Carter): Auth priority (SSH Key > API key > JWT)
    - Pattern 2 (Carter): TTL caching (JWT exp extraction)
    - Pattern 3 (Bauer): API wrapper (crash-safe, .meta.rc checks)
    - Pattern 4 (Beale): Constraint validation (Hellodeolu v6)
    """

    # Canonical Registry (Metadata Mapping - Hellodeolu v7 Consolidation)
    _REGISTRY: ClassVar[dict[str, Any]] = {
        "discover_sites": {
            "path": "api/v1/sites",
            "method": "GET",
            "guardian": "Bauer",
            "description": "Discover all sites in controller",
        },
        "get_devices": {
            "path": "integration/v1/sites/{site_uuid}/devices",
            "method": "GET",
            "guardian": "Carter",
            "description": "Get devices (APs, switches, USG) for site",
        },
        "get_networks_v2": {
            "path": "api/s/{site_id}/rest/networkconf",
            "method": "GET",
            "guardian": "Beale",
            "description": "Modern API for networks/VLANs (Hellodeolu v7)",
        },
        "get_wifi_broadcasts": {
            "path": "api/s/{site_id}/rest/wlanconf",
            "method": "GET",
            "guardian": "Carter",
            "description": "Modern API for SSIDs/WiFi configuration",
        },
        "get_firewall_zones": {
            "path": "api/s/{site_id}/rest/firewallzone",
            "method": "GET",
            "guardian": "Beale",
            "description": "Modern API for Zone-Based Firewall zones",
        },
        "get_acl_rules": {
            "path": "api/s/{site_id}/rest/firewallrule",
            "method": "GET",
            "guardian": "Beale",
            "description": "Modern API for Access Control Lists",
        },
        "get_firewall_rules": {
            "path": "api/s/{site_id}/rest/firewallrule",
            "method": "GET",
            "guardian": "Beale",
            "description": "Fetch firewall rules (Hellodeolu: Unlimited)",
        },
        "create_firewall_rule": {
            "path": "api/s/{site_id}/rest/firewallrule",
            "method": "POST",
            "guardian": "Beale",
            "description": "Create firewall rule (requires Beale validation)",
        },
        "get_networks": {
            "path": "api/s/{site_id}/rest/networkconf",
            "method": "GET",
            "guardian": "Beale",
            "description": "Fetch VLANs and network configs (Hellodeolu constraint: max 10)",
        },
        "create_network": {
            "path": "api/s/{site_id}/rest/networkconf",
            "method": "POST",
            "guardian": "Beale",
            "description": "Create VLAN (requires Beale validation)",
        },
        "get_wlan_configs": {
            "path": "api/s/{site_id}/rest/wlanconf",
            "method": "GET",
            "guardian": "Carter",
            "description": "Fetch wireless network configurations (Max 4 SSIDs)",
        },
        "create_wlan_config": {
            "path": "api/s/{site_id}/rest/wlanconf",
            "method": "POST",
            "guardian": "Carter",
            "description": "Create new SSID (requires Carter validation)",
        },
        "adopt_device": {
            "path": "api/s/{site_id}/cmd/devmgr",
            "method": "POST",
            "guardian": "Bauer",
            "description": "Adopt unadopted device by MAC address",
        },
        "get_backup_settings": {
            "path": "api/s/{site_id}/rest/setting/autobackup",
            "method": "GET",
            "guardian": "Bauer",
            "description": "Fetch autobackup settings",
        },
        "get_system_settings": {
            "path": "api/s/{site_id}/rest/setting/mgmt",
            "method": "GET",
            "guardian": "Bauer",
            "description": "Fetch general system management settings (SSH, MDNS)",
        },
        "get_security_settings": {
            "path": "api/s/{site_id}/rest/setting/connectivity",
            "method": "GET",
            "guardian": "Beale",
            "description": "Fetch global security and connectivity settings",
        },
        "get_port_profiles": {
            "path": "api/s/{site_id}/rest/portconf",
            "method": "GET",
            "guardian": "Beale",
            "description": "Fetch switch port profiles (VLAN assignments, PoE)",
        },
        "get_device_ports": {
            "path": "api/s/{site_id}/stat/device",
            "method": "GET",
            "guardian": "Beale",
            "description": "Fetch device-specific port status and configurations",
        },
        "get_clients": {
            "path": "api/s/{site_id}/stat/sta",
            "method": "GET",
            "guardian": "Bauer",
            "description": "Fetch active clients table",
        },
        "get_devices_legacy": {
            "path": "api/s/{site_id}/stat/device",
            "method": "GET",
            "guardian": "Bauer",
            "description": "Get devices using legacy stat API (includes _id)",
        },
        "update_device": {
            "path": "api/s/{site_id}/rest/device/{device_id}",
            "method": "PUT",
            "guardian": "Beale",
            "description": "Update device configuration (Legacy REST API)",
        },
    }

    def __init__(
        self,
        host: str,
        port: int = 443,
        api_key: str | None = None,
        username: str | None = None,
        password: str | None = None,
        ssh_key: str | None = None,
    ) -> None:
        """Initialize client with auth preference detection."""
        self.host = host
        self.port = port
        self.api_key = api_key
        self.username = username
        self.password = password
        self.ssh_key = ssh_key

        # API endpoints
        self.api_base = f"https://{host}:{port}/proxy/network"
        self.auth_base = f"https://{host}:{port}/api/auth"

        # Site identifiers
        self.site_id = "default"
        self.site_uuid: str | None = None

        # Auth state (Pattern 2: TTL caching)
        self.jwt_token: str | None = None
        self.csrf_token: str | None = None
        self.jwt_exp: int | None = None

        # Cookie jar for session auth
        self.cookie_jar = http.cookiejar.CookieJar()

        # SSL context (homelab: no verification)
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

        # Self-Validation (Bauer Phase 2)
        self._validate_registry()

        # Pattern 1: Detect auth mode
        self._detect_auth_mode()

    def _validate_registry(self) -> None:
        """Verify Canonical Registry integrity (Bauer)."""
        required_keys = ["path", "method", "guardian"]
        for name, details in self._REGISTRY.items():
            for key in required_keys:
                if key not in details:
                    raise UniFiConfigError(f"CRITICAL: Registry corruption in '{name}' - missing '{key}'")

            # Path convention check (Pillar 5)
            path = details["path"]
            if not (path.startswith("api/") or path.startswith("integration/") or path.startswith("proxy/")):
                raise UniFiConfigError(f"CRITICAL: Registry path '{path}' violates naming convention")

        self._log_audit("registry_validated", {"count": len(self._REGISTRY)})

    def _detect_auth_mode(self) -> None:
        """Determine auth priority: API key (v7) > SSH > JWT. (Pattern 1: Carter)."""
        if self.simulation_mode:
            self.auth_mode = "simulation"
            self._log_audit("auth_mode_detected", {"mode": "simulation"})
            return

        # Phase 2: Prioritize API Key (Leo v1.0.0 Blueprint)
        if self.api_key:
            self.auth_mode = "api_key"
            self._log_audit("auth_mode_detected", {"mode": "api_key"})
        elif self.ssh_key and self.username:
            self.auth_mode = "ssh_key"
            self._log_audit("auth_mode_detected", {"mode": "ssh_key"})
            try:
                self.ensure_jwt_fresh()
            except UniFiAuthError:
                if self.password:
                    self._log_audit("ssh_key_failed", {"fallback": "jwt_password"})
                    self.auth_mode = "jwt"
                    self.ensure_jwt_fresh()
                else:
                    raise
        elif self.username and self.password:
            self.auth_mode = "jwt"
            self._log_audit("auth_mode_detected", {"mode": "jwt"})
            self.ensure_jwt_fresh()
        else:
            msg = "No valid auth parameters: API_KEY (preferred), SSH_KEY, or credentials missing"
            raise UniFiConfigError(msg)

    def _log_audit(self, event: str, data: dict[str, Any]) -> None:
        """Record audit event."""
        self.audit_log.append({"timestamp": time.time(), "event": event, "data": data})

    def _extract_jwt_exp(self, token: str) -> int | None:
        """Decode JWT and extract exp claim (seconds since epoch). (Pattern 2: TTL)."""
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
            exp = claims.get("exp")
            return int(exp) if isinstance(exp, int | float) else None
        except (ValueError, KeyError, TypeError):
            return None

    def ensure_jwt_fresh(self) -> None:
        """Check JWT expiry; re-login if expired. (Pattern 2: TTL caching)."""
        if self.auth_mode == "api_key":
            return

        # Try to load from local cache file first
        # Use a user-specific path to avoid insecure /tmp usage (S108)
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
                # Silent failure on cache load is acceptable; fall back to login
                pass

        if self.jwt_token and self.jwt_exp:
            current_time = int(time.time())
            if current_time < self.jwt_exp - 60:  # 60-second buffer
                self._log_audit("auth_cache_hit", {"ttl_remaining": self.jwt_exp - current_time})
                return

        self._log_audit(
            "auth_expired_or_missing",
            {"attempting_re_login": True, "mode": self.auth_mode},
        )

        if self.auth_mode == "ssh_key":
            self._login_ssh()
        else:
            self._login_jwt()

        # Save to local cache file
        if self.jwt_token:
            try:
                with open(cache_path, "w") as f:
                    json.dump(
                        {
                            "host": self.host,
                            "jwt": self.jwt_token,
                            "exp": self.jwt_exp,
                            "csrf": self.csrf_token,
                        },
                        f,
                    )
            except OSError:
                # Failing to save cache is non-critical for operation
                pass

    def _login_ssh(self) -> None:
        """Authenticate via SSH and extract JWT. (Pattern X: Carter)."""
        if not self.ssh_key or not self.username:
            raise UniFiAuthError("SSH key or username missing for SSH login")

        self._log_audit("ssh_auth_attempt", {"host": self.host, "user": self.username})

        # Determine if ssh_key is a path or content
        key_path = self.ssh_key
        cleanup_needed = False
        if "-----BEGIN" in self.ssh_key:
            import tempfile
            import textwrap

            # Ensure key is correctly dedented if it came from a YAML block
            clean_key = textwrap.dedent(self.ssh_key).strip() + "\n"

            with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
                f.write(clean_key)
                key_path = f.name
                cleanup_needed = True
            os.chmod(key_path, 0o600)

        # Execute SSH command to read JWT from UniFi OS
        # Command prioritized for UDM/UCKV2: /data/unifi-os/unifi-os.jwt
        cmd = [
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "ConnectTimeout=10",
            "-i",
            key_path,
            f"{self.username}@{self.host}",
            "cat /data/unifi-os/unifi-os.jwt",
        ]

        try:
            # S603/S607: Use full path to ssh if possible, but 'ssh' is standard
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)  # noqa: S603
            if result.returncode != 0:
                error_detail = result.stderr.strip() or f"Return code {result.returncode}"
                raise UniFiAuthError(f"SSH command failed: {error_detail}")

            self.jwt_token = result.stdout.strip()
            if not self.jwt_token:
                raise UniFiAuthError("SSH command returned empty token")

            self.jwt_exp = self._extract_jwt_exp(self.jwt_token)

            # Sync cookie jar for subsequent HTTPS requests
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

            self._log_audit("ssh_auth_success", {"exp": self.jwt_exp})

        except subprocess.TimeoutExpired:
            raise UniFiAuthError("SSH authentication timed out after 15s") from None
        except (RuntimeError, ValueError) as e:
            if isinstance(e, UniFiAuthError):
                raise
            raise UniFiAuthError(f"SSH authentication failed: {e}") from None
        finally:
            if cleanup_needed:
                try:
                    os.remove(key_path)
                except OSError:
                    pass

    def _login_jwt(self) -> None:
        """Authenticate via JWT/CSRF session flow. (Pattern 2: TTL)."""
        if not self.username or not self.password:
            raise UniFiAuthError("Credentials missing for JWT login")

        url = f"{self.auth_base}/login"
        data = json.dumps({"username": self.username, "password": self.password}).encode("utf-8")
        req = urllib.request.Request(  # noqa: S310
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with self.opener.open(req, timeout=10) as r:
                response_text = r.read().decode("utf-8")
                try:
                    json.loads(response_text)
                except (ValueError, json.JSONDecodeError):
                    pass

            # Extract token from cookie jar
            self.jwt_token = None
            for cookie in self.cookie_jar:
                if cookie.name == "TOKEN":
                    self.jwt_token = cookie.value
                    break

            if not self.jwt_token:
                raise UniFiAuthError("JWT token not found in login response cookies")

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
                raise UniFiAuthError("CSRF token not found in JWT claims")

            self._log_audit(
                "login_success",
                {"ttl_seconds": ((self.jwt_exp - int(time.time())) if self.jwt_exp else None)},
            )

        except urllib.error.HTTPError as e:
            error_msg = f"Login failed: HTTP {e.code} {e.reason}"
            self._log_audit("login_failed", {"http_code": e.code, "reason": str(e.reason)})
            raise UniFiAuthError(error_msg) from e
        except UniFiAuthError:
            raise
        except (OSError, ValueError) as e:
            error_msg = f"Login error: {e!s}"
            self._log_audit("login_error", {"error": str(e)})
            raise UniFiAuthError(error_msg) from e

    def api_call(
        self,
        endpoint: str,
        method: str | None = None,
        data: dict[str, Any] | list[Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Make authenticated API call. (Pattern 3: Bauer wrapper).

        Args:
            endpoint: Registry name (e.g., 'get_devices') or raw path.
            method: HTTP method (optional if using Registry name).
            data: Payload dictionary for POST/PUT.
            **kwargs: Template variables for Registry path (e.g., device_id=...).
        """
        response: Any = None
        # Registry Lookup
        if endpoint in self._REGISTRY:
            details = self._REGISTRY[endpoint]
            path_template = details["path"]
            method = method or details["method"]

            # Ensure site_uuid is resolved if template needs it
            if "{site_uuid}" in path_template and not self.site_uuid:
                self.discover_sites()

            # Formatting template with available identifiers and kwargs
            endpoint = path_template.format(site_id=self.site_id, site_uuid=self.site_uuid or "PENDING", **kwargs)

        method = method or "GET"

        if self.simulation_mode:
            self._log_audit("simulation_api_call", {"endpoint": endpoint, "method": method})
            if "stat/device" in endpoint:
                return {
                    "meta": {"rc": "ok"},
                    "data": [
                        {
                            "mac": "fc:ec:da:4e:1c:bd",
                            "model": "US8P60",
                            "name": "Switch-Homelab",
                            "device_id": "mock_id_123",
                            "_id": "mock_id_123",
                            "port_table": [
                                {
                                    "port_idx": 4,
                                    "name": "Port 4",
                                    "native_networkconf_id": "vlan1",
                                }
                            ],
                        }
                    ],
                }
            if "sites" in endpoint:
                return {
                    "meta": {"rc": "ok"},
                    "data": [
                        {
                            "name": "default",
                            "desc": "Default",
                            "_id": "site_default_id",
                            "id": "site_default_id",
                        }
                    ],
                }
            if "networkconf" in endpoint:
                return {
                    "meta": {"rc": "ok"},
                    "data": [
                        {
                            "name": "Default",
                            "vlan": 1,
                            "_id": "vlan1_id",
                            "purpose": "corporate",
                        },
                        {
                            "name": "Servers",
                            "vlan": 10,
                            "_id": "vlan10_id",
                            "purpose": "corporate",
                        },
                        {
                            "name": "Trusted",
                            "vlan": 30,
                            "_id": "vlan30_id",
                            "purpose": "corporate",
                        },
                        {
                            "name": "Guest",
                            "vlan": 80,
                            "_id": "vlan80_id",
                            "purpose": "corporate",
                        },
                        {
                            "name": "IoT",
                            "vlan": 90,
                            "_id": "vlan90_id",
                            "purpose": "corporate",
                        },
                    ],
                }
            if "apgroup" in endpoint:
                return {
                    "meta": {"rc": "ok"},
                    "data": [{"name": "All APs", "_id": "apgroup_all_id"}],
                }
            if "rest/wlanconf" in endpoint:
                return {
                    "meta": {"rc": "ok"},
                    "data": [
                        {"name": "Old_SSID_1", "_id": "old1", "security": "wpapsk"},
                        {"name": "Old_SSID_2", "_id": "old2", "security": "wpapsk"},
                        {"name": "Old_SSID_3", "_id": "old3", "security": "wpapsk"},
                        {"name": "Old_SSID_4", "_id": "old4", "security": "wpapsk"},
                    ],
                }
            if "firewall/zone" in endpoint:
                return {
                    "meta": {"rc": "ok"},
                    "data": [
                        {"name": "Internal", "_id": "zone_internal_id"},
                        {"name": "Management", "_id": "zone_mgmt_id"},
                        {"name": "Servers", "_id": "zone_servers_id"},
                        {"name": "Trusted", "_id": "zone_trusted_id"},
                        {"name": "IoT", "_id": "zone_iot_id"},
                    ],
                }
            if "acl-rules" in endpoint:
                return {"meta": {"rc": "ok"}, "data": []}
            if "object-oriented-network-config" in endpoint:
                # Handle both singular and plural for simulation
                return {"meta": {"rc": "ok"}, "data": []}

            return {"meta": {"rc": "ok"}, "data": []}

        url = f"{self.api_base}/{endpoint}"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (RylanLabs; IaC-Validator)",
        }

        if self.auth_mode == "api_key":
            headers["X-API-Key"] = self.api_key or ""
        else:
            self.ensure_jwt_fresh()
            headers["X-CSRF-Token"] = self.csrf_token or ""

        request_data = None
        if data is not None:
            request_data = json.dumps(data).encode("utf-8")

        req = urllib.request.Request(url, data=request_data, headers=headers, method=method)  # noqa: S310

        try:
            with self.opener.open(req, timeout=10) as r:
                response_text = r.read().decode("utf-8")
                # Handle 204 No Content or empty responses (Pattern 3: Bauer)
                if not response_text:
                    response = {"meta": {"rc": "ok"}, "data": []}
                else:
                    response = json.loads(response_text)

        except urllib.error.HTTPError as e:
            if e.code == 401:
                self._log_audit("api_call_unauthorized", {"endpoint": endpoint})
                raise UniFiAuthError(f"Unauthorized (401) on {endpoint}") from e

            # Bauer: Capture full body for audit logging
            raw_body = e.read().decode("utf-8")
            try:
                error_response = json.loads(raw_body)
                msg = error_response.get("meta", {}).get("msg", raw_body)
                # If V2 style error
                if "error" in error_response:
                    msg = error_response["error"].get("message", "V2 API Error")
            except (ValueError, json.JSONDecodeError, AttributeError):
                msg = raw_body or str(e.reason)

            self._log_audit(
                "api_call_http_error",
                {"endpoint": endpoint, "code": e.code, "body": raw_body},
            )
            raise UniFiAPIError(f"HTTP {e.code} on {endpoint}: {msg}") from e

        except (OSError, ValueError) as e:
            self._log_audit("api_call_exception", {"endpoint": endpoint, "error": str(e)})
            raise UniFiAPIError(f"Request failed on {endpoint}: {e!s}") from e

        # Pattern 3: Check UniFi's error wrapper (.meta.rc == "error")
        if isinstance(response, dict):
            if response.get("meta", {}).get("rc") == "error":
                error_msg = response.get("meta", {}).get("msg", "Unknown error")
                self._log_audit("api_call_unifi_error", {"endpoint": endpoint, "msg": error_msg})
                raise UniFiAPIError(f"{endpoint}: {error_msg}")

        self._log_audit("api_call_success", {"endpoint": endpoint, "method": method})
        return response

    def discover_sites(self) -> list[dict[str, Any]]:
        """Get list of sites (Integration API v1). Discover and cache site UUID."""
        result = self.api_call("integration/v1/sites")
        sites = result.get("data", [])
        if sites:
            self.site_uuid = sites[0]["id"]
            self._log_audit("site_discovered", {"site_uuid": self.site_uuid, "count": len(sites)})
        return cast("list[dict[str, Any]]", sites)

    def get_devices(self) -> list[dict[str, Any]]:
        """Get devices for current site (requires site_uuid from discover_sites())."""
        if not self.site_uuid:
            self.discover_sites()

        result = self.api_call(f"integration/v1/sites/{self.site_uuid}/devices")
        devices = result.get("data", [])
        self._log_audit("devices_fetched", {"count": len(devices)})
        return cast("list[dict[str, Any]]", devices)

    def get_networks_v2(self) -> list[dict[str, Any]]:
        """Get networks using modern v1 API (Hellodeolu v7)."""
        if not self.site_uuid:
            self.discover_sites()
        result = self.api_call("get_networks_v2")
        networks = result.get("data", [])
        self._log_audit("networks_v2_fetched", {"count": len(networks)})
        return networks  # type: ignore[no-any-return]

    def get_wifi_broadcasts(self) -> list[dict[str, Any]]:
        """Get WiFi Broadcasts (SSIDs) using modern v1 API."""
        if not self.site_uuid:
            self.discover_sites()
        result = self.api_call("get_wifi_broadcasts")
        broadcasts = result.get("data", [])
        self._log_audit("wifi_broadcasts_fetched", {"count": len(broadcasts)})
        return broadcasts  # type: ignore[no-any-return]

    def get_firewall_zones(self) -> list[dict[str, Any]]:
        """Get custom firewall zones using modern v1 API."""
        if not self.site_uuid:
            self.discover_sites()
        result = self.api_call("get_firewall_zones")
        zones = result.get("data", [])
        self._log_audit("firewall_zones_fetched", {"count": len(zones)})
        return zones  # type: ignore[no-any-return]

    def get_acl_rules(self) -> list[dict[str, Any]]:
        """Get ACL rules using modern v1 API."""
        if not self.site_uuid:
            self.discover_sites()
        result = self.api_call("get_acl_rules")
        rules = result.get("data", [])
        self._log_audit("acl_rules_fetched", {"count": len(rules)})
        return rules  # type: ignore[no-any-return]

    def get_firewall_rules(self) -> list[dict[str, Any]]:
        """Get firewall rules for current site (uses site shortname 'default')."""
        result = self.api_call(f"api/s/{self.site_id}/rest/firewallrule")
        rules = result.get("data", [])
        self._log_audit("firewall_rules_fetched", {"count": len(rules)})
        return rules  # type: ignore[no-any-return]

    def create_firewall_rule(self, rule_data: dict[str, Any], check_mode: bool = False) -> dict[str, Any]:
        """Create firewall rule with idempotency."""
        name = rule_data.get("name")

        # Map internal keys to UniFi API keys
        payload = rule_data.copy()
        if "state" in payload:
            if payload["state"] == "enabled":
                payload["enabled"] = True
            payload.pop("state")

        # Handle VLAN resolution
        if "src_vlan" in payload or "dst_vlan" in payload:
            networks = self.get_networks()
            if "src_vlan" in payload:
                vlan_val = payload.pop("src_vlan")
                # Handle both string and int comparison (Pattern: Robust Types)
                net_id = next(
                    (
                        n["_id"]
                        for n in networks
                        if (str(vlan_val) == "1" and n.get("name") == "Default")
                        or (str(n.get("vlan")) == str(vlan_val))
                    ),
                    None,
                )
                if not net_id:
                    raise UniFiError(f"Source VLAN {vlan_val} not found")
                payload["src_networkconf_id"] = net_id
                payload["src_networkconf_type"] = "NETv4"

            if "dst_vlan" in payload:
                vlan_val = payload.pop("dst_vlan")
                # Handle both string and int comparison (Pattern: Robust Types)
                net_id = next(
                    (
                        n["_id"]
                        for n in networks
                        if (str(vlan_val) == "1" and n.get("name") == "Default")
                        or (str(n.get("vlan")) == str(vlan_val))
                    ),
                    None,
                )
                if not net_id:
                    raise UniFiError(f"Destination VLAN {vlan_val} not found")
                payload["dst_networkconf_id"] = net_id
                payload["dst_networkconf_type"] = "NETv4"

        # Handle IPs
        if "dst_ip" in payload:
            payload["dst_address"] = payload.pop("dst_ip")
        if "src_ip" in payload:
            payload["src_address"] = payload.pop("src_ip")

        # Handle Firewall Groups
        if "src_group" in payload or "dst_group" in payload:
            groups = self.get_firewall_groups()
            if "src_group" in payload:
                group_name = payload.pop("src_group")
                group_id = next((g["_id"] for g in groups if g.get("name") == group_name), None)
                if not group_id:
                    raise UniFiError(f"Source Group '{group_name}' not found")
                payload["src_firewallgroup_ids"] = [group_id]
                # Default to ADDRV4 if it's an address group, but the API expects the ID

            if "dst_group" in payload:
                group_name = payload.pop("dst_group")
                group_id = next((g["_id"] for g in groups if g.get("name") == group_name), None)
                if not group_id:
                    raise UniFiError(f"Destination Group '{group_name}' not found")
                payload["dst_firewallgroup_ids"] = [group_id]

        # Set mandatory type for network links (Pattern: Post-Probe Discovery)
        payload["src_networkconf_type"] = payload.get("src_networkconf_type", "NETv4")
        payload["dst_networkconf_type"] = payload.get("dst_networkconf_type", "NETv4")

        # Defaults matching successful API capture (Pattern: Robust Schemas)
        defaults = {
            "enabled": True,
            "protocol": "all",
            "logging": False,
            "setting_preference": "auto",
            "state_established": False,
            "state_invalid": False,
            "state_new": False,
            "state_related": False,
        }
        for k, v in defaults.items():
            if k not in payload:
                payload[k] = v

        # Idempotency Check
        current_rules = self.get_firewall_rules()
        for rule in current_rules:
            if rule.get("name") == name:
                self._log_audit("firewall_idempotent_skip", {"name": name})
                return {
                    "changed": False,
                    "data": rule,
                    "msg": "Firewall rule already exists",
                }

        # Rule Index (Auto-increment based on ruleset)
        # Try omitting rule_index on UXG models if range fails

        if check_mode:
            return {
                "changed": True,
                "msg": "Firewall rule would be created (check_mode)",
            }

        result = self.api_call(f"api/s/{self.site_id}/rest/firewallrule", method="POST", data=payload)
        self._log_audit("firewall_rule_created", {"rule_name": name})
        return {"changed": True, "data": result}

    def delete_firewall_rule(self, rule_name: str) -> dict[str, Any]:
        """Delete firewall rule by name."""
        rules = self.get_firewall_rules()
        rule = next((r for r in rules if r.get("name") == rule_name), None)

        if not rule:
            self._log_audit("firewall_delete_skip", {"name": rule_name, "reason": "not_found"})
            return {"changed": False, "msg": f"Firewall rule {rule_name} not found"}

        rule_id = rule["_id"]
        result = self.api_call(f"api/s/{self.site_id}/rest/firewallrule/{rule_id}", method="DELETE")
        self._log_audit("firewall_rule_deleted", {"rule_name": rule_name, "rule_id": rule_id})
        return {"changed": True, "data": result}

    def get_firewall_groups(self) -> list[dict[str, Any]]:
        """Get firewall groups (address groups, port groups)."""
        result = self.api_call(f"api/s/{self.site_id}/rest/firewallgroup")
        groups = result.get("data", [])
        self._log_audit("firewall_groups_fetched", {"count": len(groups)})
        return groups  # type: ignore[no-any-return]

    def create_firewall_group(self, group_data: dict[str, Any]) -> dict[str, Any]:
        """Create a firewall group with idempotency."""
        name = group_data.get("name")

        # Idempotency Check
        current_groups = self.get_firewall_groups()
        for group in current_groups:
            if group.get("name") == name:
                self._log_audit("firewall_group_idempotent_skip", {"name": name})
                return {
                    "changed": False,
                    "data": group,
                    "msg": "Firewall group already exists",
                }

        payload = group_data.copy()
        if "members" in payload:
            payload["group_members"] = payload.pop("members")

        # API requires group_type (Pattern: Post-Probe Discovery)
        if "group_type" not in payload:
            payload["group_type"] = payload.get("type", "address-group")

        result = self.api_call(f"api/s/{self.site_id}/rest/firewallgroup", method="POST", data=payload)
        self._log_audit("firewall_group_created", {"group_name": name})
        return {"changed": True, "data": result}

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ZONE-BASED FIREWALL (V2) — Hellodeolu v7 Capability
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_zones(self) -> list[dict[str, Any]]:
        """Get firewall zones (UXG-Max/V2 API)."""
        result = self.api_call(f"v2/api/site/{self.site_id}/firewall/zone")
        # V2 API often returns the list directly or in a specific wrapper
        zones = result if isinstance(result, list) else result.get("data", [])
        self._log_audit("zones_fetched", {"count": len(zones)})
        return zones

    def create_zone(self, zone_data: dict[str, Any], check_mode: bool = False) -> dict[str, Any]:
        """Create or update a firewall zone."""
        name = zone_data.get("name")
        network_ids = zone_data.get("network_ids", [])

        current_zones = self.get_zones()
        zone = next((z for z in current_zones if z.get("name") == name), None)

        if zone:
            # Check for changes (idempotency)
            if set(zone.get("network_ids", [])) == set(network_ids):
                return {
                    "changed": False,
                    "data": zone,
                    "msg": "Zone already exists and is up to date",
                }

            if check_mode:
                return {"changed": True, "msg": f"Zone '{name}' would be updated"}

            # Update existing zone
            zone_id = zone["_id"]
            result = self.api_call(
                f"v2/api/site/{self.site_id}/firewall/zone/{zone_id}",
                method="PUT",
                data=zone_data,
            )
            return {"changed": True, "data": result}

        if check_mode:
            return {"changed": True, "msg": f"Zone '{name}' would be created"}

        result = self.api_call(f"v2/api/site/{self.site_id}/firewall/zone", method="POST", data=zone_data)
        self._log_audit("zone_created", {"name": name})
        return {"changed": True, "data": result}

    def delete_zone(self, zone_name: str) -> dict[str, Any]:
        """Delete firewall zone by name."""
        zones = self.get_zones()
        zone = next((z for z in zones if z.get("name") == zone_name), None)

        if not zone:
            return {"changed": False, "msg": f"Zone '{zone_name}' not found"}

        if zone.get("default_zone"):
            raise UniFiError(f"Cannot delete default zone '{zone_name}'")

        zone_id = zone["_id"]
        result = self.api_call(f"v2/api/site/{self.site_id}/firewall/zone/{zone_id}", method="DELETE")
        return {"changed": True, "data": result}

    def get_zone_matrix(self) -> list[dict[str, Any]]:
        """Get firewall zone matrix."""
        result = self.api_call(f"v2/api/site/{self.site_id}/firewall/zone-matrix")
        matrix = result if isinstance(result, list) else result.get("data", [])
        return matrix

    def update_zone_matrix(self, matrix_data: list[dict[str, Any]]) -> dict[str, Any]:
        """Update the entire zone matrix (Bulk)."""
        # UXG-Max usually expects the full matrix in a PUT request
        result = self.api_call(
            f"v2/api/site/{self.site_id}/firewall/zone-matrix",
            method="PUT",
            data=matrix_data,
        )
        return {"changed": True, "data": result}

    def get_firewall_policies(self, query_params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Get V2 Firewall Policies (ZBF Rules)."""
        url = f"v2/api/site/{self.site_id}/firewall-policies"
        if query_params:
            import urllib.parse

            url += "?" + urllib.parse.urlencode(query_params)
        result = self.api_call(url)
        policies = result if isinstance(result, list) else result.get("data", [])
        self._log_audit("firewall_policies_fetched", {"count": len(policies)})
        return policies

    def delete_firewall_policy(self, policy_id: str) -> dict[str, Any]:
        """Delete V2 Firewall Policy by ID."""
        result = self.api_call(f"v2/api/site/{self.site_id}/firewall-policies/{policy_id}", method="DELETE")
        self._log_audit("firewall_policy_deleted", {"policy_id": policy_id})
        return {"changed": True, "data": result}

    def create_firewall_policy(self, policy_data: dict[str, Any], check_mode: bool = False) -> dict[str, Any]:
        """Create or update a V2 Firewall Policy (ZBF Rule)."""
        name = policy_data.get("name")
        current_policies = self.get_firewall_policies()

        # Identify by name (V2 rules focus on names for UI consistency)
        policy = next((p for p in current_policies if p.get("name") == name), None)

        if policy:
            # Simple idempotency: check action and zones
            if (
                policy.get("action") == policy_data.get("action")
                and policy.get("source", {}).get("zone_id") == policy_data.get("source", {}).get("zone_id")
                and policy.get("destination", {}).get("zone_id") == policy_data.get("destination", {}).get("zone_id")
            ):
                return {
                    "changed": False,
                    "data": policy,
                    "msg": "Policy already exists",
                }

            if check_mode:
                return {"changed": True, "msg": f"Policy '{name}' would be updated"}

            policy_id = policy["_id"]
            result = self.api_call(
                f"v2/api/site/{self.site_id}/firewall-policies/{policy_id}",
                method="PUT",
                data=policy_data,
            )
            return {"changed": True, "data": result}

        if check_mode:
            return {"changed": True, "msg": f"Policy '{name}' would be created"}

        result = self.api_call(
            f"v2/api/site/{self.site_id}/firewall-policies",
            method="POST",
            data=policy_data,
        )
        self._log_audit("firewall_policy_created", {"name": name})
        return {"changed": True, "data": result}

    def get_network_members_groups(self) -> list[dict[str, Any]]:
        """Get V2 Network Members Groups (MAC Groups)."""
        result = self.api_call(f"v2/api/site/{self.site_id}/network-members-group")
        groups = result if isinstance(result, list) else result.get("data", [])
        return groups

    def create_network_members_group(self, group_data: dict[str, Any], check_mode: bool = False) -> dict[str, Any]:
        """Create or update a Network Members Group."""
        name = group_data.get("name")
        current_groups = self.get_network_members_groups()
        group = next((g for g in current_groups if g.get("name") == name), None)

        if group:
            if set(group.get("members", [])) == set(group_data.get("members", [])):
                return {"changed": False, "data": group, "msg": "Group already exists"}

            if check_mode:
                return {"changed": True, "msg": f"Group '{name}' would be updated"}

            group_id = group["id"]
            result = self.api_call(
                f"v2/api/site/{self.site_id}/network-members-group/{group_id}",
                method="PUT",
                data=group_data,
            )
            return {"changed": True, "data": result}

        if check_mode:
            return {"changed": True, "msg": f"Group '{name}' would be created"}

        result = self.api_call(
            f"v2/api/site/{self.site_id}/network-members-group",
            method="POST",
            data=group_data,
        )
        return {"changed": True, "data": result}

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TARGET OBJECTS (V2) — Hellodeolu v7 Dynamic Groups
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_target_objects(self) -> list[dict[str, Any]]:
        """Fetch V2 Target Objects (Consolidated OONC endpoint)."""
        try:
            # Hellodeolu v7: Use plural plural object-oriented-network-configs for listing
            res = self.api_call(f"v2/api/site/{self.site_id}/object-oriented-network-configs")
            data = res if isinstance(res, list) else res.get("data", [])
            self._log_audit("target_objects_fetched", {"count": len(data)})
            return data
        except (RuntimeError, ValueError) as e:
            self._log_audit("target_objects_fetch_failed", {"error": str(e)})
            # Fallback to granular rules if consolidated endpoint fails
            results: list[dict[str, Any]] = []
            endpoints = [
                "v2/api/site/default/acl-rules",
                "v2/api/site/default/qos-rules",
            ]
            for ep in endpoints:
                try:
                    res = self.api_call(ep)
                    data = res if isinstance(res, list) else res.get("data", [])
                    results.extend(data)
                except (OSError, RuntimeError, ValueError):
                    continue
            return results

    def create_target_object(self, obj_data: dict[str, Any], check_mode: bool = False) -> dict[str, Any]:
        """Create or update a V2 Target Object (Dynamic Group)."""
        name = obj_data.get("name")

        # Check Mode support
        if check_mode:
            return {"changed": True, "msg": f"Object '{name}' would be managed"}

        # V2 creation usually uses the singular endpoint for the config container
        result = self.api_call(
            f"v2/api/site/{self.site_id}/object-oriented-network-config",
            method="POST",
            data=obj_data,
        )
        self._log_audit("target_object_created", {"name": name})
        return {"changed": True, "data": result}

    def delete_target_object(self, obj_name: str) -> dict[str, Any]:
        """Delete a V2 Target Object by name."""
        objects = self.get_target_objects()
        # V2 objects often use 'id' instead of '_id'
        target = next((obj for obj in objects if obj.get("name") == obj_name), None)

        if not target:
            return {"changed": False, "msg": f"Object '{obj_name}' not found"}

        obj_id = target.get("id") or target.get("_id")
        # Deletion often uses the configuration endpoint with the ID
        result = self.api_call(
            f"v2/api/site/{self.site_id}/object-oriented-network-config/{obj_id}",
            method="DELETE",
        )
        return {"changed": True, "data": result}

    def get_networks(self) -> list[dict[str, Any]]:
        """Get VLANs and network configurations."""
        result = self.api_call(f"api/s/{self.site_id}/rest/networkconf")
        networks = result.get("data", [])
        self._log_audit("networks_fetched", {"count": len(networks)})
        return networks  # type: ignore[no-any-return]

    def get_settings(self, key: str | None = None) -> list[dict[str, Any]]:
        """Get global controller settings. (Pattern: Beale)."""
        endpoint = f"api/s/{self.site_id}/rest/setting"
        if key:
            endpoint += f"/{key}"
        result = self.api_call(endpoint)
        settings = result.get("data", [])
        self._log_audit("settings_fetched", {"key": key, "count": len(settings)})
        return settings  # type: ignore[no-any-return]

    def get_v2_setting(self, path: str) -> dict[str, Any]:
        """Get a v2 setting (e.g. global/config/network)."""
        # The base URL logic already prepends proxy/network
        # Path should be something like v2/api/site/default/global/config/network
        result = self.api_call(path.lstrip("/"))
        # v2 endpoints often return the object directly without 'data' wrapper
        return result if isinstance(result, dict) else {}

    def update_v2_setting(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Update a v2 setting with idempotency."""
        current = self.get_v2_setting(path)

        # Merge payload into existing object
        data = current.copy()
        data.update(payload)

        if data == current:
            self._log_audit("v2_setting_idempotent_skip", {"path": path})
            return {
                "changed": False,
                "msg": "Setting already matches target configuration",
            }

        result = self.api_call(path.lstrip("/"), method="PUT", data=data)
        self._log_audit("v2_setting_updated", {"path": path})
        return {"changed": True, "data": result}

    def update_setting(self, key: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Update a global setting by key."""
        # First, find the current setting object
        current = self.get_settings(key)
        if not current:
            raise UniFiAPIError(f"Setting key '{key}' not found; cannot update")

        current_obj = current[0]
        setting_id = current_obj["_id"]

        # Merge payload into the existing object to preserve all fields
        data = current_obj.copy()
        data.update(payload)

        # Idempotency check: if data hasn't changed, skip the API call
        if data == current_obj:
            self._log_audit("setting_idempotent_skip", {"key": key})
            return {
                "changed": False,
                "msg": "Setting already matches target configuration",
            }

        result = self.api_call(
            f"api/s/{self.site_id}/rest/setting/{key}/{setting_id}",
            method="PUT",
            data=data,
        )
        self._log_audit("setting_updated", {"key": key})
        return {"changed": True, "data": result}

    def create_network(self, network_data: dict[str, Any], check_mode: bool = False) -> dict[str, Any]:
        """Create VLAN or network configuration with idempotency."""
        name = network_data.get("name")
        vlan_id = network_data.get("vlan_id") or network_data.get("vlan")

        # Map internal keys to UniFi API keys
        payload = network_data.copy()
        if "vlan_id" in payload:
            payload["vlan"] = payload.pop("vlan_id")
        if "subnet" in payload:
            payload["ip_subnet"] = payload.pop("subnet")

        # Default required fields for corporate VLANs
        if "vlan" in payload:
            payload["vlan_enabled"] = True
        if payload.get("purpose") == "corporate":
            if "dhcpd_enabled" not in payload:
                payload["dhcpd_enabled"] = True
            if "networkgroup" not in payload:
                payload["networkgroup"] = "LAN"

        if check_mode:
            return {
                "changed": True,
                "msg": f"Network {name} would be created (check_mode)",
            }

        # Idempotency Check
        current_networks = self.get_networks()
        for net in current_networks:
            match_name = net.get("name") == name
            net_vlan = net.get("vlan")

            match_vlan = False
            if vlan_id is not None:
                if net_vlan is not None:
                    try:
                        match_vlan = int(net_vlan) == int(vlan_id)
                    except (ValueError, TypeError):
                        pass
                elif str(vlan_id) == "1" and net.get("name") == "Default":
                    # Special case: VLAN 1 matches Default network (untagged)
                    match_vlan = True

            if match_name or match_vlan:
                # Compare critical properties (Bauer Verification)
                match_subnet = net.get("ip_subnet") == payload.get("ip_subnet")
                if match_subnet:
                    msg = (
                        f"Network already exists and matches (Match Name: {match_name}, "
                        f"Match VLAN: {match_vlan}, Match Subnet: {match_subnet})"
                    )
                    self._log_audit(
                        "network_idempotent_skip",
                        {"name": name, "vlan": vlan_id, "found_vlan": net_vlan},
                    )
                    return {"changed": False, "data": net, "msg": msg}
                else:
                    # Update existing network
                    self._log_audit(
                        "network_update_trigger",
                        {"name": name, "reason": "subnet_mismatch"},
                    )
                    result = self.api_call(
                        f"api/s/{self.site_id}/rest/networkconf/{net['_id']}",
                        method="PUT",
                        data=payload,
                    )
                    return {
                        "changed": True,
                        "data": result,
                        "msg": "Network updated (subnet mismatch)",
                    }

        result = self.api_call(f"api/s/{self.site_id}/rest/networkconf", method="POST", data=payload)
        self._log_audit("network_created", {"network_name": name})
        return {"changed": True, "data": result}

    def get_wlan_configs(self) -> list[dict[str, Any]]:
        """Get wireless network configurations."""
        result = self.api_call(f"api/s/{self.site_id}/rest/wlanconf")
        wlan_configs = result.get("data", [])
        self._log_audit("wlan_configs_fetched", {"count": len(wlan_configs)})
        return wlan_configs  # type: ignore[no-any-return]

    def create_wlan_config(self, wlan_data: dict[str, Any], check_mode: bool = False) -> dict[str, Any]:
        """Create a new wireless network configuration with idempotency."""
        name = wlan_data.get("name")

        # Normalize payload
        payload = wlan_data.copy()
        if "vlan_id" in payload:
            # For WLAN, we need to find the networkconf_id of the VLAN
            vlan_id = payload.pop("vlan_id")
            networks = self.get_networks()
            net_id = next((n["_id"] for n in networks if str(n.get("vlan")) == str(vlan_id)), None)
            if net_id:
                payload["networkconf_id"] = net_id
            else:
                raise UniFiAPIError(f"VLAN {vlan_id} not found; cannot link SSID {name}")

        # Ensure security is set (UniFi defaults to open otherwise)
        if "x_passphrase" not in payload and "passphrase" in payload:
            payload["x_passphrase"] = payload.pop("passphrase")

        # Hellodeolu v7/UXG-Max Mapping Alignment
        if "multicast_enhance" in payload:
            payload["mcastenhance_enabled"] = payload.pop("multicast_enhance")
        if "guest_policy" in payload:
            policy = payload.pop("guest_policy")
            payload["is_guest"] = policy == "enabled"
        if "device_isolation" in payload:
            payload["l2_isolation"] = payload.pop("device_isolation")

        # Default security settings for UXG-Max baseline
        if payload.get("security") == "wpapsk":
            payload.setdefault("wpa_mode", "wpa2")
            payload.setdefault("pmf_mode", "optional")
            payload.setdefault("wpa3_support", True)
            payload.setdefault("wpa3_transition", True)

        payload.setdefault("wlan_bands", ["2g", "5g"])
        payload.setdefault("dtim_mode", "default")
        payload.setdefault("setting_preference", "manual")
        if "ap_group_ids" not in payload:
            payload["ap_group_mode"] = "all"
            # Try to find default group
            groups: list[dict[str, Any]] = []
            try:
                # Capture suggests this endpoint for v2 Groups on fresh OS
                groups_resp = self.api_call("v2/api/site/default/apgroups")
                groups = groups_resp if isinstance(groups_resp, list) else groups_resp.get("data", [])
            except UniFiAPIError:
                try:
                    # Fallback to legacy
                    groups_resp = self.api_call(f"api/s/{self.site_id}/rest/apgroup")
                    groups = groups_resp.get("data", [])
                except UniFiAPIError:
                    pass

            default_group = next((g["_id"] for g in groups if g.get("name") == "All APs"), None)
            if not default_group and groups:
                default_group = groups[0].get("_id")

            if default_group:
                payload["ap_group_ids"] = [default_group]
                self._log_audit("wlan_ap_group_found", {"id": default_group})
            else:
                self._log_audit(
                    "wlan_ap_group_missing",
                    {"msg": "Omit ap_group_ids; relying on default"},
                )

        # Idempotency Check
        current_wlans = self.get_wlan_configs()
        for wlan in current_wlans:
            if wlan.get("name") == name:
                self._log_audit("wlan_idempotent_skip", {"ssid": name})
                return {"changed": False, "data": wlan, "msg": "SSID already exists"}

        if check_mode:
            return {
                "changed": True,
                "msg": f"SSID {name} would be created (check_mode)",
            }

        result = self.api_call(f"api/s/{self.site_id}/rest/wlanconf", method="POST", data=payload)
        self._log_audit("wlan_config_created", {"ssid": name})
        return {"changed": True, "data": result}

    def adopt_device(self, mac: str) -> dict[str, Any]:
        """Adopt a device by MAC address."""
        result = self.api_call(
            f"api/s/{self.site_id}/cmd/devmgr",
            method="POST",
            data={"mac": mac, "cmd": "adopt"},
        )
        self._log_audit("device_adopted", {"mac": mac})
        return result if isinstance(result, dict) else {}

    def delete_network(self, network_id: str) -> dict[str, Any]:
        """Delete a network configuration."""
        result = self.api_call(f"api/s/{self.site_id}/rest/networkconf/{network_id}", method="DELETE")
        self._log_audit("network_deleted", {"network_id": network_id})
        return {"changed": True, "data": result}

    def delete_wlan_config(self, wlan_id: str) -> dict[str, Any]:
        """Delete a wireless network configuration."""
        result = self.api_call(f"api/s/{self.site_id}/rest/wlanconf/{wlan_id}", method="DELETE")
        self._log_audit("wlan_deleted", {"wlan_id": wlan_id})
        return {"changed": True, "data": result}

    def update_device(self, device_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Update device configuration (e.g., port overrides, aliases)."""
        result = self.api_call(f"api/s/{self.site_id}/rest/device/{device_id}", method="PUT", data=payload)
        self._log_audit("device_updated", {"device_id": device_id})
        return {"changed": True, "data": result}

    def configure_port(self, device_mac: str, port_config: dict[str, Any], check_mode: bool = False) -> dict[str, Any]:
        """Configure a specific switch port via port_overrides."""
        # 1. Find device
        devices = self.api_call(f"api/s/{self.site_id}/stat/device")
        device = next((d for d in devices.get("data", []) if d.get("mac") == device_mac), None)
        if not device:
            raise UniFiAPIError(f"Device with MAC {device_mac} not found")

        device_id = device["_id"]
        port_idx = port_config.get("port_idx")
        if port_idx is None:
            raise UniFiAPIError("port_idx is required for configure_port")

        # 2. Extract current overrides
        overrides = device.get("port_overrides", [])
        existing_override = next((o for o in overrides if o.get("port_idx") == port_idx), None)

        # 3. Resolve Native VLAN if provided
        new_override = existing_override.copy() if existing_override else {"port_idx": port_idx}

        if "name" in port_config:
            new_override["name"] = port_config["name"]

        if "native_vlan" in port_config:
            vlan = port_config["native_vlan"]
            networks = self.get_networks()
            # Find by VLAN ID or Name if it's 'Default' (which often has no VLAN ID)
            net = next((n for n in networks if str(n.get("vlan")) == str(vlan)), None)
            if not net and str(vlan) == "1":
                net = next((n for n in networks if n.get("name") == "Default"), None)

            if not net:
                raise UniFiAPIError(f"VLAN {vlan} not found in network list")
            new_override["native_networkconf_id"] = net["_id"]
            new_override["setting_preference"] = "manual"
            new_override["forward"] = "customize"

        if "isolation" in port_config:
            new_override["isolation"] = port_config["isolation"]
            new_override["setting_preference"] = "manual"
            new_override["forward"] = "customize"

        # Idempotency check: compare new_override vs existing_override
        if existing_override and all(new_override.get(k) == existing_override.get(k) for k in new_override):
            self._log_audit("port_config_idempotent_skip", {"mac": device_mac, "port": port_idx})
            return {
                "changed": False,
                "msg": f"Port {port_idx} already matches desired configuration",
            }

        if check_mode:
            return {
                "changed": True,
                "msg": f"Port {port_idx} on {device_mac} would be updated (check_mode)",
            }

        # 4. Merge and update
        if existing_override:
            overrides = [new_override if o.get("port_idx") == port_idx else o for o in overrides]
        else:
            overrides.append(new_override)

        result = self.update_device(device_id, {"port_overrides": overrides})
        self._log_audit("port_configured", {"mac": device_mac, "port_idx": port_idx})
        return {"changed": True, "data": result}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ANSIBLE MODULE INTERFACE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def main() -> None:
    """Ansible module entry point."""
    if not AnsibleModule:
        raise RuntimeError("Ansible module not available")

    module = AnsibleModule(
        argument_spec={
            "host": {"type": "str", "required": True},
            "port": {"type": "int", "default": 443},
            "api_key": {"type": "str", "no_log": True},
            "username": {"type": "str"},
            "password": {"type": "str", "no_log": True},
            "ssh_key": {"type": "str", "no_log": True},
            "action": {
                "type": "str",
                "choices": [
                    "get_sites",
                    "get_devices",
                    "get_devices_legacy",
                    "get_firewall_rules",
                    "create_firewall_rule",
                    "delete_firewall_rule",
                    "get_firewall_groups",
                    "create_firewall_group",
                    "get_networks",
                    "create_network",
                    "delete_network",
                    "get_wlan_configs",
                    "create_wlan_config",
                    "delete_wlan_config",
                    "get_settings",
                    "update_setting",
                    "get_v2_setting",
                    "update_v2_setting",
                    "get_firewall_zones",
                    "get_zones",
                    "create_zone",
                    "delete_zone",
                    "delete_firewall_zone",
                    "get_zone_matrix",
                    "update_zone_matrix",
                    "get_firewall_policies",
                    "create_firewall_policy",
                    "delete_firewall_policy",
                    "get_network_members_groups",
                    "create_network_members_group",
                    "get_target_objects",
                    "create_target_object",
                    "delete_target_object",
                    "adopt_device",
                    "update_device",
                    "configure_port",
                    "validate_constraints",
                    "api_call",
                ],
            },
            "site_uuid": {"type": "str"},
            "rule_data": {"type": "dict"},
            "network_data": {"type": "dict"},
            "wlan_data": {"type": "dict"},
            "port_data": {"type": "dict"},
            "setting_data": {"type": "dict"},
            "setting_key": {"type": "str"},
            "network_id": {"type": "str"},
            "wlan_id": {"type": "str"},
            "device_id": {"type": "str"},
            "mac": {"type": "str"},
            "path": {"type": "str"},
            "method": {"type": "str", "default": "GET"},
            "data": {"type": "dict"},
        },
        supports_check_mode=True,
    )

    try:
        client = UniFiClient(
            module.params["host"],
            module.params["port"],
            module.params["api_key"],
            module.params["username"],
            module.params["password"],
            module.params["ssh_key"],
        )

        action = module.params["action"]

        if action == "get_sites":
            sites = client.discover_sites()
            module.exit_json(changed=False, data=sites, audit_log=client.audit_log)

        elif action == "get_devices":
            devices = client.get_devices()
            module.exit_json(changed=False, data=devices, audit_log=client.audit_log)

        elif action == "get_devices_legacy":
            result = client.api_call("get_devices_legacy")
            devices = result.get("data", [])
            module.exit_json(changed=False, data=devices, audit_log=client.audit_log)

        elif action == "get_firewall_rules":
            rules = client.get_firewall_rules()
            module.exit_json(changed=False, data=rules, audit_log=client.audit_log)

        elif action == "create_firewall_rule":
            result = client.create_firewall_rule(module.params["rule_data"], check_mode=module.check_mode)
            module.exit_json(
                changed=result.get("changed", True),
                data=result.get("data"),
                msg=result.get("msg"),
                audit_log=client.audit_log,
            )

        elif action == "get_zones" or action == "get_firewall_zones":
            zones = client.get_zones()
            module.exit_json(changed=False, data=zones, audit_log=client.audit_log)

        elif action == "create_zone":
            result = client.create_zone(module.params["data"], check_mode=module.check_mode)
            module.exit_json(
                changed=result.get("changed", True),
                data=result.get("data"),
                msg=result.get("msg"),
                audit_log=client.audit_log,
            )

        elif action == "delete_zone" or action == "delete_firewall_zone":
            # Support both direct 'data.name' and direct 'name' (for flexibility)
            name = module.params["data"].get("name") if module.params.get("data") else module.params.get("name")
            result = client.delete_zone(name)
            module.exit_json(
                changed=result.get("changed", True),
                data=result.get("data"),
                msg=result.get("msg"),
                audit_log=client.audit_log,
            )

        elif action == "get_zone_matrix":
            result = client.get_zone_matrix()
            module.exit_json(changed=False, data=result, audit_log=client.audit_log)

        elif action == "update_zone_matrix":
            result = client.update_zone_matrix(module.params["data"])
            module.exit_json(
                changed=result.get("changed", True),
                data=result.get("data"),
                audit_log=client.audit_log,
            )

        elif action == "get_firewall_policies":
            # Pass query_params if provided in 'data'
            result = client.get_firewall_policies(query_params=module.params.get("data"))
            module.exit_json(changed=False, data=result, audit_log=client.audit_log)

        elif action == "create_firewall_policy":
            result = client.create_firewall_policy(module.params["data"], check_mode=module.check_mode)
            module.exit_json(**result, audit_log=client.audit_log)

        elif action == "delete_firewall_policy":
            # Support policy_id in params or in data
            policy_id = module.params.get("policy_id") or (module.params.get("data") or {}).get("policy_id")
            result = client.delete_firewall_policy(policy_id)  # type: ignore[arg-type]
            module.exit_json(**result, audit_log=client.audit_log)

        elif action == "get_network_members_groups":
            result = client.get_network_members_groups()
            module.exit_json(changed=False, data=result, audit_log=client.audit_log)

        elif action == "create_network_members_group":
            result = client.create_network_members_group(module.params["data"], check_mode=module.check_mode)
            module.exit_json(**result, audit_log=client.audit_log)

        elif action == "get_target_objects":
            objects = client.get_target_objects()
            module.exit_json(changed=False, data=objects, audit_log=client.audit_log)

        elif action == "create_target_object":
            result = client.create_target_object(module.params["data"], check_mode=module.check_mode)
            module.exit_json(
                changed=result.get("changed", True),
                data=result.get("data"),
                audit_log=client.audit_log,
            )

        elif action == "delete_target_object":
            result = client.delete_target_object(module.params["data"].get("name"))
            module.exit_json(
                changed=result.get("changed", True),
                data=result.get("data"),
                audit_log=client.audit_log,
            )

        elif action == "delete_firewall_rule":
            result = client.delete_firewall_rule(module.params["rule_data"].get("name"))
            module.exit_json(
                changed=result.get("changed", True),
                data=result.get("data"),
                msg=result.get("msg"),
                audit_log=client.audit_log,
            )

        elif action == "get_firewall_groups":
            groups = client.get_firewall_groups()
            module.exit_json(changed=False, data=groups, audit_log=client.audit_log)

        elif action == "create_firewall_group":
            result = client.create_firewall_group(module.params["data"])
            module.exit_json(
                changed=result.get("changed", True),
                data=result.get("data"),
                audit_log=client.audit_log,
            )

        elif action == "get_networks":
            networks = client.get_networks()
            module.exit_json(changed=False, data=networks, audit_log=client.audit_log)

        elif action == "get_settings":
            settings = client.get_settings(module.params.get("setting_key"))
            module.exit_json(changed=False, data=settings, audit_log=client.audit_log)

        elif action == "update_setting":
            result = client.update_setting(module.params["setting_key"], module.params["setting_data"])
            module.exit_json(
                changed=result.get("changed", True),
                data=result.get("data"),
                audit_log=client.audit_log,
            )

        elif action == "get_v2_setting":
            result = client.get_v2_setting(module.params["path"])
            module.exit_json(changed=False, data=result, audit_log=client.audit_log)

        elif action == "update_v2_setting":
            result = client.update_v2_setting(module.params["path"], module.params["data"])
            module.exit_json(
                changed=result.get("changed", True),
                data=result.get("data"),
                audit_log=client.audit_log,
            )

        elif action == "create_network":
            result = client.create_network(module.params["network_data"], check_mode=module.check_mode)
            module.exit_json(
                changed=result.get("changed", True),
                data=result.get("data"),
                msg=result.get("msg"),
                audit_log=client.audit_log,
            )

        elif action == "delete_network":
            result = client.delete_network(module.params["network_id"])
            module.exit_json(
                changed=result.get("changed", True),
                data=result.get("data"),
                audit_log=client.audit_log,
            )

        elif action == "get_wlan_configs":
            configs = client.get_wlan_configs()
            module.exit_json(changed=False, data=configs, audit_log=client.audit_log)

        elif action == "create_wlan_config":
            result = client.create_wlan_config(module.params["wlan_data"], check_mode=module.check_mode)
            module.exit_json(
                changed=result.get("changed", True),
                data=result.get("data"),
                msg=result.get("msg"),
                audit_log=client.audit_log,
            )

        elif action == "delete_wlan_config":
            result = client.delete_wlan_config(module.params["wlan_id"])
            module.exit_json(
                changed=result.get("changed", True),
                data=result.get("data"),
                audit_log=client.audit_log,
            )

        elif action == "configure_port":
            result = client.configure_port(
                module.params["mac"],
                module.params["port_data"],
                check_mode=module.check_mode,
            )
            module.exit_json(
                changed=result.get("changed", True),
                data=result.get("data"),
                msg=result.get("msg"),
                audit_log=client.audit_log,
            )

        elif action == "adopt_device":
            result = client.adopt_device(module.params["mac"])
            module.exit_json(changed=True, data=result, audit_log=client.audit_log)

        elif action == "update_device":
            # Usage: action=update_device device_id=... data={name: ...}
            device_id = module.params.get("device_id")
            data = module.params.get("data")
            if not device_id or not data:
                module.fail_json(msg="update_device requires 'device_id' and 'data'")

            # Bauer Check: Simulation or live
            if module.check_mode:
                module.exit_json(changed=True, msg=f"Device {device_id} would be updated with {data}")

            result = client.api_call("update_device", device_id=device_id, data=data)
            module.exit_json(changed=True, data=result, audit_log=client.audit_log)

        elif action == "validate_constraints":
            rules = client.get_firewall_rules()
            networks = client.get_networks()
            state = {"firewall_rules": rules, "networks": networks}
            validation = UniFiConstraintValidator.validate_all(state)
            has_violations = any(not v.get("valid", True) for v in validation.values())

            if has_violations:
                module.fail_json(
                    msg="Constraint violations detected",
                    validation=validation,
                    audit_log=client.audit_log,
                )
            else:
                module.exit_json(changed=False, validation=validation, audit_log=client.audit_log)

        elif action == "api_call":
            result = client.api_call(
                module.params["path"],
                method=module.params["method"],
                data=module.params["data"],
            )
            module.exit_json(changed=True, data=result, audit_log=client.audit_log)

        else:
            module.fail_json(msg=f"Unknown action: {action}")

    except UniFiError as e:
        module.fail_json(msg=str(e), exit_code=e.exit_code)
    except (OSError, ValueError, TypeError) as e:
        module.fail_json(msg=f"Unexpected error: {e!s}")


if __name__ == "__main__":
    main()
