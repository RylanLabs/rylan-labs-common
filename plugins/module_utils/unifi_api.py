from __future__ import annotations

import requests
from typing import Any, Dict, List, cast


class UnifiAPI:
    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = 443,
        site: str = "default",
        verify_ssl: bool = False,
    ) -> None:
        self.host: str = host
        self.port: int = port
        self.username: str = username
        self.password: str = password
        self.site: str = site
        self.verify_ssl: bool = verify_ssl
        self.session: requests.Session = requests.Session()
        protocol = "https" if port in [443, 8443] or verify_ssl else "http"
        self.base_url: str = f"{protocol}://{host}:{port}/proxy/network/api/s/{site}"
        self.logged_in: bool = False

    def login(self) -> bool:
        protocol = "https" if self.port in [443, 8443] or self.verify_ssl else "http"
        login_url = f"{protocol}://{self.host}:{self.port}/api/auth/login"
        payload: Dict[str, Any] = {"username": self.username, "password": self.password}
        response = self.session.post(login_url, json=payload, verify=self.verify_ssl)
        if response.status_code == 200:
            self.logged_in = True
            return True
        return False

    def get_devices(self) -> List[Dict[str, Any]]:
        if not self.logged_in:
            self.login()
        url = f"{self.base_url}/stat/device"
        response = self.session.get(url, verify=self.verify_ssl)
        payload = response.json()
        if isinstance(payload, dict):
            return cast(List[Dict[str, Any]], payload.get("data", []))
        return []

    def get_clients(self) -> List[Dict[str, Any]]:
        if not self.logged_in:
            self.login()
        url = f"{self.base_url}/stat/sta"
        response = self.session.get(url, verify=self.verify_ssl)
        payload = response.json()
        if isinstance(payload, dict):
            return cast(List[Dict[str, Any]], payload.get("data", []))
        return []

    def update_device(self, device_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.logged_in:
            self.login()
        url = f"{self.base_url}/rest/device/{device_id}"
        response = self.session.put(url, json=data, verify=self.verify_ssl)
        payload = response.json()
        if isinstance(payload, dict):
            return cast(Dict[str, Any], payload)
        return {}
