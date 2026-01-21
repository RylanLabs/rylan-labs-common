#!/usr/bin/env python3
# Copyright: (c) 2026, RylanLabs
# GNU General Public License v3.0+

"""
UniFi Dynamic Inventory Script

Implements Manifest-First Merging:
1. Load device-manifest.yml (Git source of truth)
2. Query UniFi Controller API (live state)
3. Merge with Git precedence (Verification Domain principle: trust but verify)

Features:
- TTL caching (reduces API calls)
- Offline mode (uses cached data)
- Tier-based grouping (T1-T4)
- Guardian role assignment

Usage:
  ansible-inventory -i inventory/unifi_dynamic_inventory.py --list
  ansible-inventory -i inventory/unifi_dynamic_inventory.py --host <hostname>

Environment Variables:
  UNIFI_CONTROLLER_URL: Controller URL (required)
  UNIFI_API_KEY: API key (required)
  UNIFI_CACHE_TTL: Cache TTL in seconds (default: 300)
  UNIFI_OFFLINE_MODE: Use cached data only (default: false)
"""

import argparse
import json
import os
import signal
import sys
import time
from datetime import datetime, timedelta
from typing import Any

try:
    import requests
    import yaml
except ImportError as e:
    sys.stderr.write(f"❌ ERROR: Required package missing: {e}\n")
    sys.stderr.write("   Fix: pip install requests pyyaml\n")
    sys.exit(2)

# Suppress SSL warnings if verify=False (homelab)
try:
    import urllib3
    from urllib3.exceptions import InsecureRequestWarning

    urllib3.disable_warnings(InsecureRequestWarning)
except ImportError:
    pass

# Env vars (Vault integration)
UNIFI_HOST: str = os.getenv("UNIFI_HOST", "unifi.local")
UNIFI_PORT: str = os.getenv("UNIFI_PORT", "443")
UNIFI_USER: str | None = os.getenv("UNIFI_USER")
UNIFI_PASS: str | None = os.getenv("UNIFI_PASS")
UNIFI_API_KEY: str | None = os.getenv("UNIFI_API_KEY") or os.getenv("UNIFI_TOKEN")
UNIFI_SITE: str = os.getenv("UNIFI_SITE", "default")
UNIFI_VERIFY_SSL: bool = os.getenv("UNIFI_VERIFY_SSL", "false").lower() == "true"
MANIFEST_PATH: str = os.getenv("MANIFEST_PATH", "inventory/device-manifest.yml")
TIMEOUT: int = int(os.getenv("UNIFI_TIMEOUT", "10"))
RATELIMIT_DELAY: float = float(os.getenv("UNIFI_RATELIMIT_DELAY", "1.0"))
CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))
CACHE_PATH: str = os.getenv("CACHE_PATH", ".cache/unifi_inventory.json")
LAST_SEEN_MINUTES: int = int(os.getenv("LAST_SEEN_MINUTES", "30"))
INCLUDE_CLIENTS: bool = os.getenv("INCLUDE_CLIENTS", "false").lower() == "true"
UNIFI_OFFLINE_MODE: bool = os.getenv("UNIFI_OFFLINE_MODE", "false").lower() == "true"


class UniFiAPIError(Exception):
    """Custom exception for UniFi API failures."""


class UniFiInventory:
    """Manage UniFi API query and manifest merge."""

    def __init__(self) -> None:
        """Initialize UniFi API manager with configuration."""
        self.base_url: str = f"https://{UNIFI_HOST}:{UNIFI_PORT}"
        self.session: requests.Session = requests.Session()
        self.session.verify = UNIFI_VERIFY_SSL
        self.session.headers.update({"Accept": "application/json"})
        self.devices: list[dict[str, Any]] = []
        self.clients: list[dict[str, Any]] = []
        self.static_manifest: dict[str, Any] = {}
        self.audit_log: list[str] = []
        self.cache_hit: bool = False
        self.site_id: str | None = None
        self.controller_type: str = "unknown"  # 'legacy' or 'unifi_os'
        self.last_request_time: float = 0
        self.csrf_token: str | None = None  # For UniFi OS CSRF protection

    def log_audit(self, message: str) -> None:
        """Log audit with timestamp to stderr."""
        timestamp: str = datetime.now().isoformat()
        entry: str = f"[{timestamp}] {message}"
        self.audit_log.append(entry)
        sys.stderr.write(f"{entry}\n")

    def handle_ratelimit(self, retry_after: str | None = None) -> None:
        """Handle rate limiting (429 responses)."""
        delay = float(retry_after) if retry_after else RATELIMIT_DELAY
        self.log_audit(f"Rate limited; waiting {delay}s before retry")
        time.sleep(delay)

    def cleanup(self, signum: int | None = None, frame: Any | None = None) -> None:
        """Cleanup on exit/signal."""
        self.log_audit("Cleanup: Closing session")
        self.session.close()
        if signum:
            sys.exit(130)  # SIGINT

    def authenticate(self) -> None:
        """Authenticate with UniFi controller (auto-detect type)."""
        if UNIFI_API_KEY:
            self.log_audit("[Auth] Using API Key authentication")
            return

        if not UNIFI_USER or not UNIFI_PASS:
            raise UniFiAPIError

        # Try UniFi OS first (port 443, /api/auth/login)
        self.log_audit(f"[Auth] Attempting UniFi OS: {self.base_url}/api/auth/login")
        login_url: str = f"{self.base_url}/api/auth/login"
        payload: dict[str, str] = {"username": UNIFI_USER, "password": UNIFI_PASS}

        try:
            response = self.session.post(login_url, json=payload, timeout=TIMEOUT, verify=self.session.verify)
            if response.status_code == 429:
                self.handle_ratelimit(response.headers.get("Retry-After"))
                response = self.session.post(login_url, json=payload, timeout=TIMEOUT, verify=self.session.verify)

            if response.status_code == 200:
                self.controller_type = "unifi_os"
                self.csrf_token = response.headers.get("x-updated-csrf-token") or response.headers.get("X-Csrf-Token")
                if self.csrf_token:
                    self.session.headers.update({"X-Csrf-Token": self.csrf_token})
                    self.log_audit(f"✓ CSRF token captured: {self.csrf_token[:16]}...")
                self.log_audit("✓ Auth successful (UniFi OS)")
                return
        except requests.RequestException as e:
            self.log_audit(f"UniFi OS auth failed: {e}")

        # Fall back to legacy API (/api/login)
        self.log_audit(f"[Auth] Attempting legacy: {self.base_url}/api/login")
        login_url = f"{self.base_url}/api/login"
        try:
            response = self.session.post(login_url, json=payload, timeout=TIMEOUT, verify=self.session.verify)
            if response.status_code == 429:
                self.handle_ratelimit(response.headers.get("Retry-After"))
                response = self.session.post(login_url, json=payload, timeout=TIMEOUT, verify=self.session.verify)

            if response.status_code == 200:
                self.controller_type = "legacy"
                self.log_audit("✓ Auth successful (Legacy Controller)")
                return
        except requests.RequestException as e:
            self.log_audit(f"Legacy auth failed: {e}")

        raise UniFiAPIError

    def get_site_id(self) -> str:
        """Get site UUID (controller-type aware)."""
        if self.site_id:
            return self.site_id

        if self.controller_type == "legacy":
            self.site_id = "default"
            self.log_audit("[Sites] Using implicit site 'default' (legacy controller)")
            return self.site_id

        # UniFi OS: Query /proxy/network/api/v1/sites
        url: str = f"{self.base_url}/proxy/network/api/v1/sites"
        if UNIFI_API_KEY:
            self.session.headers.update({"X-API-Key": UNIFI_API_KEY})

        try:
            self.log_audit(f"[Sites] Querying: {url}")
            time.sleep(self.get_ratelimit_delay())
            response = self.session.get(url, timeout=TIMEOUT, verify=self.session.verify)
            self.last_request_time = time.time()

            if response.status_code == 429:
                self.handle_ratelimit(response.headers.get("Retry-After"))
                response = self.session.get(url, timeout=TIMEOUT, verify=self.session.verify)
                self.last_request_time = time.time()

            response.raise_for_status()
            data: dict[str, Any] = response.json()
            sites: list[dict[str, Any]] = data.get("data", [])

            for site in sites:
                ref: str = site.get("internalReference", "")
                name: str = site.get("name", "")
                if ref == UNIFI_SITE or name.lower() == UNIFI_SITE.lower():
                    site_uuid: str = site.get("id", "")
                    self.site_id = site_uuid
                    self.log_audit(f"[Sites] Found: {name} (ID: {self.site_id})")
                    return site_uuid

            if sites:
                first_site_id: str = sites[0].get("id", "")
                self.site_id = first_site_id
                self.log_audit(f"[Sites] Using first: {sites[0].get('name')} (ID: {self.site_id})")
                return first_site_id

            raise UniFiAPIError
        except requests.RequestException as e:
            raise UniFiAPIError from e

    def get_ratelimit_delay(self) -> float:
        """Return delay since last request to enforce rate limiting."""
        elapsed = time.time() - self.last_request_time
        return max(0, RATELIMIT_DELAY - elapsed)

    def fetch_data(self, endpoint: str) -> list[dict[str, Any]]:
        """Fetch from UniFi API (controller-type aware)."""
        site_id: str = self.get_site_id()

        if self.controller_type == "unifi_os" or UNIFI_API_KEY:
            url = f"{self.base_url}/proxy/network/api/v1/sites/{site_id}/{endpoint}"
        else:
            url = f"{self.base_url}/api/s/{site_id}/stat/{endpoint}"

        try:
            self.log_audit(f"[Fetch] {endpoint}: {url}")
            time.sleep(self.get_ratelimit_delay())
            response = self.session.get(url, timeout=TIMEOUT, verify=self.session.verify)
            self.last_request_time = time.time()

            if response.status_code == 429:
                self.handle_ratelimit(response.headers.get("Retry-After"))
                response = self.session.get(url, timeout=TIMEOUT, verify=self.session.verify)
                self.last_request_time = time.time()

            response.raise_for_status()
            data: dict[str, Any] = response.json()
            result = data.get("data", []) if isinstance(data, dict) else data
            self.log_audit(f"[Fetch] {endpoint}: Retrieved {len(result)} items")
            return result if isinstance(result, list) else []
        except requests.RequestException as e:
            raise UniFiAPIError from e

    def load_cache(self) -> dict[str, Any] | None:
        """Load cache if valid."""
        if CACHE_TTL == 0 or not os.path.exists(CACHE_PATH):
            return None
        try:
            with open(CACHE_PATH, encoding="utf-8") as f:
                cache: dict[str, Any] = json.load(f)
            if datetime.fromisoformat(cache["timestamp"]) + timedelta(seconds=CACHE_TTL) > datetime.now():
                self.cache_hit = True
                self.log_audit("Cache hit")
                inventory = cache["inventory"]
                return inventory if isinstance(inventory, dict) else None
            self.log_audit("Cache stale")
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            self.log_audit(f"Cache invalid: {e}")
        return None

    def save_cache(self, inventory: dict[str, Any]) -> None:
        """Save inventory to cache."""
        if CACHE_TTL == 0:
            return
        os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
        cache: dict[str, Any] = {"timestamp": datetime.now().isoformat(), "inventory": inventory}
        try:
            with open(CACHE_PATH, "w", encoding="utf-8") as f:
                json.dump(cache, f)
            self.log_audit("Cache saved")
        except OSError as e:
            self.log_audit(f"Cache save failed: {e}")

    def load_static_manifest(self) -> None:
        """Load static manifest YAML."""
        if not os.path.exists(MANIFEST_PATH):
            self.log_audit(f"WARNING: {MANIFEST_PATH} missing. Using API only.")
            self.static_manifest = {"devices": {}, "ansible_tiers": {}}
            return
        try:
            with open(MANIFEST_PATH, encoding="utf-8") as f:
                self.static_manifest = yaml.safe_load(f) or {"devices": {}, "ansible_tiers": {}}
            self.log_audit(f"Loaded manifest: {len(self.static_manifest.get('devices', {}))} devices")
        except yaml.YAMLError as e:
            raise UniFiAPIError from e

    def merge_inventory(self) -> dict[str, Any]:
        """Merge API data with static manifest."""
        merged: dict[str, Any] = {"_meta": {"hostvars": {}}}
        static_devices: dict[str, Any] = self.static_manifest.get("devices", {})
        processed: int = 0
        api_hostnames: set[str] = set()

        for item in self.devices + self.clients:
            mac: str = (item.get("macAddress") or item.get("mac", "")).lower()
            ip: str = item.get("ipAddress") or item.get("ip", "")
            name: str = item.get("name", f"unknown-{mac[-6:]}")
            hostname: str = name.lower().replace(" ", "-")
            model: str = item.get("model", "")
            is_client: bool = "ssid" in item or item.get("isGuest", False)

            static_entry: dict[str, Any] | None = next(
                (v for k, v in static_devices.items() if v.get("mac", "").lower() == mac or k.lower() == hostname),
                None,
            )
            if static_entry:
                hostname = list(static_devices.keys())[list(static_devices.values()).index(static_entry)]

            hostvars: dict[str, Any] = {}
            if static_entry:
                static_keys = {"ansible_tier", "ministry", "boot_order", "dependencies", "comments", "role", "hardware"}
                hostvars.update({k: v for k, v in static_entry.items() if k in static_keys})

            state_str: str = item.get("state", "")
            dynamic: dict[str, Any] = {
                "ansible_host": ip,
                "mac": mac,
                "model": model,
                "firmware": item.get("firmwareVersion") or item.get("version"),
                "state": state_str,
                "state_online": state_str == "ONLINE",
                "supported": item.get("supported", True),
                "firmware_updatable": item.get("firmwareUpdatable", False),
                "features": item.get("features", []),
            }
            if is_client:
                dynamic.update({"is_wired": item.get("isWired", False), "ssid": item.get("ssid"), "vlan": item.get("vlan")})
            hostvars.update({k: v for k, v in dynamic.items() if v is not None})

            # Type detection
            model_lower: str = model.lower()
            features: list[str] = item.get("features", [])
            if "accessPoint" in features or "uap" in model_lower or "ap-" in model_lower:
                hostvars["device_type"] = "access_point"
            elif "switching" in features or "usw" in model_lower or "us " in model_lower or "us-" in model_lower:
                hostvars["device_type"] = "switch"
            elif "usg" in model_lower or "gateway" in model_lower or "udm" in model_lower:
                hostvars["device_type"] = "gateway"
            else:
                hostvars["device_type"] = "unknown"

            merged["_meta"]["hostvars"][hostname] = hostvars
            api_hostnames.add(hostname)
            processed += 1

        # Static-only fallback
        for static_hostname, static_entry_raw in static_devices.items():
            if static_hostname not in api_hostnames:
                static_entry = static_entry_raw if isinstance(static_entry_raw, dict) else {}
                static_hostvars: dict[str, Any] = {}
                static_keys = {"ansible_tier", "ministry", "boot_order", "dependencies", "comments", "role", "hardware", "ip", "mac"}
                static_hostvars.update({k: v for k, v in static_entry.items() if k in static_keys})
                if "ip" in static_entry:
                    static_hostvars["ansible_host"] = static_entry["ip"]
                merged["_meta"]["hostvars"][static_hostname] = static_hostvars
                processed += 1

        for tier, data in self.static_manifest.get("ansible_tiers", {}).items():
            group: str = tier.replace("_", "-")
            merged[group] = {"hosts": data.get("devices", []), "vars": {"ansible_tier": tier}}

        return merged

    def generate_inventory(self) -> dict[str, Any]:
        """Generate full inventory."""
        if UNIFI_OFFLINE_MODE:
            cached = self.load_cache()
            if cached:
                return cached
            raise UniFiAPIError

        cached = self.load_cache()
        if cached:
            return cached

        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)

        try:
            self.authenticate()
            self.devices = self.fetch_data("devices")
            if INCLUDE_CLIENTS:
                self.clients = self.fetch_data("clients")
        except UniFiAPIError as e:
            self.log_audit(f"⚠ API unreachable, falling back to cache/static manifest: {e}")

        self.load_static_manifest()
        inventory = self.merge_inventory()
        self.save_cache(inventory)
        return inventory


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(description="UniFi Dynamic Inventory")
    parser.add_argument("--list", action="store_true", help="Output full inventory")
    parser.add_argument("--host", help="Output vars for host")
    args = parser.parse_args()

    try:
        inv_manager = UniFiInventory()
        inventory = inv_manager.generate_inventory()

        if args.host:
            print(json.dumps(inventory["_meta"]["hostvars"].get(args.host, {}), indent=2))
        elif args.list:
            print(json.dumps(inventory, indent=2))
        else:
            sys.exit(2)
    except UniFiAPIError as e:
        sys.stderr.write(f"❌ API ERROR: {e}\n")
        sys.exit(1)
    finally:
        if "inv_manager" in locals():
            inv_manager.cleanup()


if __name__ == "__main__":
    main()
