# Ansible Vault Discipline — RylanLabs Canon

> Canonical standard — Credential security and automation 
> Version: v2.0.0
> Date: 2026-01-14
> Agent: Bauer (Verification) | Ministry: Security

---

## Overview

Ansible Vault must be implemented to ensure **Zero Drift** and **Zero-Bypass automation**. This discipline prevents manual password prompts from blocking CI/CD pipelines and ensures credential rotation has a manageable blast radius.

### Core Principles

1. **Passwordless Automation**: Use `vault_password_file` to enable non-interactive execution.
2. **Service Segregation**: Avoid monolithic `vault.yml` files. Segregate by service and type.
3. **No Plaintext Secrets**: Zero tolerance for unencrypted secrets in version control.

---

## Workflow Patterns

### 1. Passwordless Configuration
All repositories must configure `ansible.cfg` to point to a `.vault-pass` file. This file must be added to `.gitignore`.

```ini
[defaults]
vault_password_file = .vault-pass
```

### 2. File Segregation
Vaults must be stored in a `vaults/` directory and follow the `{service}/{credential-type}.yml` naming convention.

**Canonical Pathing**:
- `vaults/unifi/api-creds.yml`
- `vaults/proxmox/ssh-keys.yml`
- `vaults/ad/service-accounts.yml`

**Forbidden**:
- `vaults/vault.yml` (Too broad)
- `group_vars/all/vault.yml` (Rotation blast radius too high)

### 3. File Naming Linting
Enforced via `.yamllint`:
```yaml
rules:
  file-naming-convention:
    pattern: '^vaults/[a-z-]+/[a-z-]+-[a-z]+\.yml$'
```

---

## Operations (Bauer/Beale)

### Verification
`Bauer` auditors must verify that:
- `.vault-pass` is in `.gitignore`.
- No files under `vaults/` are in plaintext.
- Linting jobs pass for vault path patterns.

### Hardening
`Beale` hardening requires:
- Vault encryption with AES256.
- Distinct passwords for different environments (Production vs. Lab).
- Automatic rejection of PRs containing secrets in `group_vars/all`.

---

## Remediations
If a monolithic vault is detected:
1. **BACKUP**: Create a full backup of the existing vault.
2. **PROCESS**: Identify service-specific variables.
3. **APPLY**: Extract variables into segregated vault files.
4. **VERIFY**: Run playbooks with restricted vault access to ensure no missing dependencies.
