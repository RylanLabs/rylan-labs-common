# Credential Rotation Discipline — RylanLabs Canon

> Canonical standard — 8-Phase Immutable Rotation Sequence
> Version: v2.0.0
> Date: 2026-01-14
> Agent: Bauer (Verification) | Domain: Audit

---

## The 8-Phase Rotation Sequence

To ensure **Zero Drift** and **Reversibility**, all credential rotations must follow the immutable 8-phase sequence. This prevents "blind rotations" that lead to service outages.

### Phase 1: BACKUP
Create an encrypted backup of the current vault and relevant configurations.
- **Verification**: `check_backup_exists`

### Phase 2: GENERATE
Generate new credentials/keys using approved algorithms (e.g., Ed25519, AES256).
- **Hardening**: Use high-entropy sources.

### Phase 3: ENCRYPT
Encrypt the new credentials using Ansible Vault.
- **Verification**: Ensure no plaintext leaks in audit logs.

### Phase 4: VALIDATE
Pre-flight check of the new vault files against the target inventory.
- **Tool**: `validate-rotation-readiness.sh`

### Phase 5: DEPLOY
Distribute the new credentials to the target infrastructure (e.g., AD, Proxmox, UniFi).

### Phase 6: ACTIVATE
Update the active configuration to use the new credentials.

### Phase 7: COMMIT
Commit the encrypted changes to version control with structured audit logs.

### Phase 8: AUDIT
Verify end-to-end connectivity and update `.audit/rotation/history.json`.

---

## Anti-Patterns (Beale-Blocked)

- **Skipping Backups**: Rotating without a rollback path is a Trinity violation.
- **In-place Overwrites**: Rotating by overwriting files without a history trail.
- **Unvalidated Deploys**: Deploying credentials without a `Bauer` pre-flight check.

---

## Observability

Rotation status is tracked in `.audit/rotation/status.json`.
A "GREEN" status requires:
1. `current_version` matches `deployed_version`.
2. `last_audit_timestamp` is within the last 24 hours.
3. `reversibility_path_verified` is true.
