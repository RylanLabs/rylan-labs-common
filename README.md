# rylan-labs-common

> Canonical Ansible Collection for UniFi Mesh Infrastructure

<!-- METADATA_START -->
## Repository Metadata

| Attribute | Value |
| :--- | :--- |
| **Tier** | 3 (GALAXY_COLLECTION) |
| **Dependencies** |  |
| **Maturity Level** | 4 |
| **ML5 Compliance** | 0.0/10 |
| **Guardian** | Security Council |
| **Last Updated** | 2026-02-05T20:45:09Z |

---

<!-- METADATA_END -->

## Overview

This collection extracts roles, modules, and plugins from the RylanLabs flagship repository into a reusable Tier 3 module.

## Roles

- `identity_role`: Managed Carter identity and GPG verification.
- `verification_role`: Idempotent drift checks for UniFi controllers.
- `hardening_role`: Automated VLAN isolation and firewall rules.

## Installation

```bash
ansible-galaxy collection install rylanlabs.unifi
```
