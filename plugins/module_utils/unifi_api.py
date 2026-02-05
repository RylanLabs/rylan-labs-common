# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import requests

class UnifiAPI(object):
    def __init__(self, host, username, password, port=443, site='default', verify_ssl=False):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.site = site
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.base_url = "https://{}:{}/proxy/network/api/s/{}".format(host, port, site)
        self.logged_in = False

    def login(self):
        login_url = "https://{}:{}/api/auth/login".format(self.host, self.port)
        payload = {
            'username': self.username,
            'password': self.password
        }
        response = self.session.post(login_url, json=payload, verify=self.verify_ssl)
        if response.status_code == 200:
            self.logged_in = True
            return True
        return False

    def get_devices(self):
        if not self.logged_in:
            self.login()
        url = "{}/stat/device".format(self.base_url)
        response = self.session.get(url, verify=self.verify_ssl)
        return response.json().get('data', [])

    def get_clients(self):
        if not self.logged_in:
            self.login()
        url = "{}/stat/sta".format(self.base_url)
        response = self.session.get(url, verify=self.verify_ssl)
        return response.json().get('data', [])

    def update_device(self, device_id, data):
        if not self.logged_in:
            self.login()
        url = "{}/rest/device/{}".format(self.base_url, device_id)
        response = self.session.put(url, json=data, verify=self.verify_ssl)
        return response.json()
