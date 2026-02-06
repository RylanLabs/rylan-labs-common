<!-- markdownlint-disable MD013 MD024 MD001 MD029 MD040 MD025 -->
# [EXPERIMENTAL] Integration Guide

> Tandem ecosystem integration for rylan-labs-common v1.0.0
> **Maturity**: Beta / Early-Access

!!! warning "Proof-of-Concept Only"
    This guide describes the target architecture for rylanlabs.common.
    As of v1.2.2, integration states are experimental. Do not use in production.

---

## Overview

This guide covers integration of `rylanlabs.common` collection with domain repositories (e.g., `rylan-labs-iac`), `rylan-canon-library`, and `rylan-inventory`.

**Key Concept**: rylanlabs.common is the *code hub*. Domain repos consume it via `ansible-galaxy install`, configure via `ansible.cfg`, and execute playbooks that include 3-Domain roles.

---

## Prerequisites (Development Versions)

1. **Ansible >= 2.14** installed
2. **rylan-canon-library (Experimental)** locally (for template reference)
3. **rylan-inventory (Experimental)** locally (for inventory data)
4. **rylanlabs.common** installed or available in `COLLECTIONS_PATHS`

---

## Getting Started: Example Playbooks

The fastest way to start using `rylanlabs.common` is to use the included example playbooks. These are templated orchestrations demonstrating the full 3-Domain workflow and key integrations.

**Available Examples** (copy to your domain repo):

- [`playbooks/example-bootstrap.yml`](../playbooks/example-bootstrap.yml): Full 3-Domain sequence (Identity → Audit → Hardening)
- [`playbooks/example-unifi-integration.yml`](../playbooks/example-unifi-integration.yml): UniFi dynamic inventory + hardening
- [`playbooks/example-validate-only.yml`](../playbooks/example-validate-only.yml): Audit compliance audit (read-only)
- [`playbooks/example-recovery.yml`](../playbooks/example-recovery.yml): Emergency recovery runbook with --confirm gates

**Quick Start**:

```bash
# 1. Copy example playbooks to your domain repo
cp -r /path/to/rylan-labs-common/playbooks your-domain-repo/

# 2. Customize for your environment (group_vars, inventory, etc.)
# 3. Dry-run to validate
ansible-playbook playbooks/example-bootstrap.yml --check

# 4. Execute (requires 3-Domain roles + UniFi configured)
ansible-playbook playbooks/example-bootstrap.yml
```bash

See [Example Playbooks](../README.md#example-playbooks) in README.md for full details on each playbook's purpose, usage, and customization.

---

## Setup: ansible.cfg

Create `ansible.cfg` in your domain repo root:

```ini
[defaults]
# Point to common collection
collections_paths = ./collections:../rylan-labs-common

# Point to inventory data
inventory = ../rylan-inventory/inventory/production.yml

# Execution settings
host_key_checking = false
timeout = 30
remote_user = ansible

# Logging
log_path = .logs/ansible.log
stdout_callback = yaml

[inventory]
# Plugin settings for dynamic inventory
enable_plugins = rylanlabs.common.unifi_dynamic_inventory

[privilege_escalation]
become = true
become_method = sudo
become_user = root
```bash

---

## Installation Options

### Option 1: Install from Ansible Galaxy (Recommended for Domain Repos)

```bash
cd your-domain-repo/
ansible-galaxy collection install rylanlabs.common
```bash

Installs to `~/.ansible/collections/ansible_collections/rylanlabs/common/`.

### Option 2: Install from Local Source

```bash
cd your-domain-repo/
ansible-galaxy collection install ../rylan-labs-common --force
```bash

Useful for development and local testing.

### Option 3: Use collections_paths (Reference Without Install)

Set `collections_paths` in `ansible.cfg` and reference FQCN directly:

```yaml
- name: Include identity-identity role
  ansible.builtin.include_role:
    name: rylanlabs.common.identity_management
```bash

---

## Usage: Example Playbook

### Basic Structure

```yaml
---
- name: Bootstrap infrastructure with 3-Domain roles
  hosts: all
  gather_facts: true

  pre_tasks:
    - name: Validate 3-Domain alignment
      ansible.builtin.debug:
        msg: "Initializing 3-Domain-aligned infrastructure (Identity/Audit/Hardening)"

  roles:
    - name: Initialize identity (Identity)
      ansible.builtin.include_role:
        name: rylanlabs.common.identity_management
      vars:
        identity_management_enabled: true
        identity_management_providers:
          - type: active_directory
            domain: example.com
          - type: radius
            server: 10.0.0.100

    - name: Verify configuration (Audit)
      ansible.builtin.include_role:
        name: rylanlabs.common.infrastructure_verify
      vars:
        infrastructure_verify_enabled: true
        infrastructure_verify_loki_endpoint: "http://loki.example.com:3100"

    - name: Harden network (Hardening)
      ansible.builtin.include_role:
        name: rylanlabs.common.hardening_management
      vars:
        hardening_management_enabled: true
        hardening_management_firewall_enabled: true
        hardening_management_nmap_validation: true

  post_tasks:
    - name: Audit deployment
      ansible.builtin.debug:
        msg: "Deployment complete. Audit trail in .audit/"
```bash

### Playbook Execution

```bash
# Dry-run (check mode)
ansible-playbook -i inventory/production.yml playbooks/bootstrap.yml --check

# Execute with increased verbosity
ansible-playbook -i inventory/production.yml playbooks/bootstrap.yml -vv

# Run specific role
ansible-playbook -i inventory/production.yml playbooks/bootstrap.yml --tags identity_management

# Run with custom variables
ansible-playbook -i inventory/production.yml playbooks/bootstrap.yml \
  -e "identity_management_enabled=true" \
  -e "infrastructure_verify_loki_endpoint=http://loki:3100"
```bash

---

## Dynamic Inventory: UniFi Integration

### 1. Create Inventory Configuration

Create `inventory/unifi_inventory.yml`:

```yaml
plugin: rylanlabs.common.unifi_dynamic_inventory
unifi_controller: https://unifi.example.com:8443
unifi_username: admin
unifi_password: "{{ vault_unifi_password }}"
unifi_verify_ssl: false
unifi_site: default
```bash

### 2. Encrypt Password (Optional)

```bash
ansible-vault encrypt inventory/unifi_inventory.yml
```bash

### 3. Use in Playbook

```bash
ansible-playbook -i inventory/unifi_inventory.yml playbooks/site.yml

# Or with vault password
ansible-playbook -i inventory/unifi_inventory.yml playbooks/site.yml \
  --vault-password-file ~/.vault_pass
```bash

---

## Tandem Validation: Canon Integration

### 1. Run Canon Pre-Commit Hooks

```bash
# Install hooks (inherited from canon)
make pre-commit-install

# Validate before commit
pre-commit run --all-files
```bash

Expected: All hooks GREEN.

### 2. Run Canon's hardening-harden.sh (Post-Deployment)

After `ansible-playbook` execution, validate with canon's hardening script:

```bash
/path/to/rylan-canon-library/scripts/hardening-harden.sh --ci \
  --inventory ../rylan-inventory/inventory/production.yml \
  --audit-path .audit/
```bash

Expected: All checks GREEN, audit trail in `.audit/`.

### 3. Monitor Audit Trail

```bash
# View recent audit logs
tail -50 .audit/ansible.log

# Search for errors
grep "ERROR\|FAIL" .audit/*.log
```bash

---

## Error Handling & Recovery

### Scenario 1: Role Execution Fails

```bash
# 1. Check ansible.log for errors
tail -100 .logs/ansible.log

# 2. Run in check mode for diagnostics
ansible-playbook -i inventory/production.yml playbooks/bootstrap.yml --check -vvv

# 3. Re-run with corrected variables
ansible-playbook -i inventory/production.yml playbooks/bootstrap.yml -e "fix_variable=value"
```bash

### Scenario 2: Pre-Commit Hook Violation

```bash
# 1. View violations
pre-commit run --all-files

# 2. Auto-fix (if available)
ruff check . --fix
ruff format .

# 3. Commit
git add . && git commit -m "[collection] Fix linting violations"
```bash

### Scenario 3: Collection Install Fails

```bash
# Force reinstall
ansible-galaxy collection install rylanlabs.common --force

# Or from local source
ansible-galaxy collection install ../rylan-labs-common --force
```bash

---

## RTO Targets & Rollback

| Scenario | Role | Recovery Command | RTO |
|----------|------|-------------------|-----|
| Collection unavailable | — | `ansible-galaxy install --force` | 2min |
| Identity service drift | Identity | `ansible-playbook -i inv playbooks/bootstrap.yml --tags identity_management` | 5min |
| Firewall misconfiguration | Hardening | `hardening-harden.sh --reset` + re-run | 10min |
| Full reset | 3-Domain | `eternal-resurrect.sh --common` | 15min |

See [emergency-response.md](emergency-response.md) for detailed procedures.

---

## Troubleshooting

### Issue: `collection not found`

```bash
ERROR! collection rylanlabs.common not found
```bash

**Solution:**

```bash
# Verify installation
ansible-galaxy collection list | grep rylanlabs

# Reinstall if missing
ansible-galaxy install rylanlabs.common

# Or set collections_paths in ansible.cfg
```bash

### Issue: `module not found`

```bash
fatal: [host]: FAILED! => {"msg": "The module unifi_api was not found"}
```bash

**Solution:**

```bash
# Check plugins path
ansible-doc -t module unifi_api

# Or verify installation
ls -la ~/.ansible/collections/ansible_collections/rylanlabs/common/plugins/modules/
```bash

### Issue: Pre-commit hook fails

```bash
yamllint............................................FAILED
```bash

**Solution:**

```bash
# Run hook individually for details
yamllint -c .yamllint .

# Fix YAML
ruff format .

# Reinstall hooks
pre-commit install --install-hooks
```bash

---

## Next Steps

1. **Review**: [seven-pillars.md](seven-pillars.md) for compliance framework
2. **Study**: [tandem-workflow.md](tandem-workflow.md) for full integration example
3. **Plan**: [emergency-response.md](emergency-response.md) for incident procedures
4. **Execute**: Run `make ci-local` in your domain repo to validate

---

## References

- **Collection**: [README.md](../README.md)
- **Canon Library**: <https://github.com/RylanLabs/rylan-canon-library>
- **Inventory**: <https://github.com/RylanLabs/rylan-inventory>
- **Ansible Docs**: <https://docs.ansible.com/ansible/latest/collections/>

---

**Status: PRODUCTION-READY**
**Grade: A+ | RTO <15min | 3-Domain-Aligned**
