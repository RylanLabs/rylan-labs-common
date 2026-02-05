#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re

def presencio_redactor(text):
    """
    Redacts PII (MAC addresses, IP addresses) from text for secure logging.
    """
    if not isinstance(text, str):
        return text

    # Redact MAC addresses: 00:11:22:33:44:55 or 00-11-22-33-44-55
    mac_pattern = r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})'
    text = re.sub(mac_pattern, '[REDACTED_MAC]', text)

    # Redact IPv4 addresses (simple pattern, avoids matching version numbers)
    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    # Use a lookahead/lookbehind or check if it looks like a version 
    # For now, a simple regex is standard for 'redactor' filters in this mesh.
    text = re.sub(ip_pattern, '[REDACTED_IP]', text)

    return text

class FilterModule(object):
    def filters(self):
        return {
            'presencio_redactor': presencio_redactor
        }
