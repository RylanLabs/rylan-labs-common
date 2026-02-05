# rylan-labs-common

> Canonical Ansible Collection for UniFi Mesh Infrastructure

<!-- METADATA_START -->
## Repository Metadata

| Attribute | Value |
| :--- | :--- |
| **Tier** | 3 (GALAXY_COLLECTION) |
| **Dependencies** | ansible.utils>=2.0.0 |
| **Maturity Level** | 7 (Autonomous Threshold) |
| **ML5 Compliance** | 7.2/10 |
| **Guardian** | Security Council |
| **Last Updated** | 2026-02-05T22:15:00Z |

---

<!-- METADATA_END -->

## Overview

This collection extracts roles, modules, and plugins from the RylanLabs flagship repository into a reusable Tier 3 module.

## Roles

- `identity_role`: Managed Carter identity and GPG verification.
- `verification_role`: Idempotent drift checks for UniFi controllers.
- `hardening_role`: (Sprint 2) Automated VLAN isolation and firewall rules.
- `recovery_role`: (Sprint 2) Emergency restoration and rollback.

## Installation

```bash
ansible-galaxy collection install rylanlabs.unifi
```
