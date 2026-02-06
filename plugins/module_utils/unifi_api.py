import requests


class UnifiAPI:
    def __init__(
        self, host, username, password, port=443, site="default", verify_ssl=False
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.site = site
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        protocol = "https" if port in [443, 8443] or verify_ssl else "http"
        self.base_url = f"{protocol}://{host}:{port}/proxy/network/api/s/{site}"
        self.logged_in = False

    def login(self):
        protocol = "https" if self.port in [443, 8443] or self.verify_ssl else "http"
        login_url = f"{protocol}://{self.host}:{self.port}/api/auth/login"
        payload = {"username": self.username, "password": self.password}
        response = self.session.post(login_url, json=payload, verify=self.verify_ssl)
        if response.status_code == 200:
            self.logged_in = True
            return True
        return False

    def get_devices(self):
        if not self.logged_in:
            self.login()
        url = f"{self.base_url}/stat/device"
        response = self.session.get(url, verify=self.verify_ssl)
        return response.json().get("data", [])

    def get_clients(self):
        if not self.logged_in:
            self.login()
        url = f"{self.base_url}/stat/sta"
        response = self.session.get(url, verify=self.verify_ssl)
        return response.json().get("data", [])

    def update_device(self, device_id, data):
        if not self.logged_in:
            self.login()
        url = f"{self.base_url}/rest/device/{device_id}"
        response = self.session.put(url, json=data, verify=self.verify_ssl)
        return response.json()
