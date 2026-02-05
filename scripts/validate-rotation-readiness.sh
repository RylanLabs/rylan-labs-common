#!/usr/bin/env bash
# Script: validate-rotation-readiness.sh
# Purpose: Pre-flight validator for credential rotation (P0 Discipline)
# Guardian: Bauer (Auditor)
# Maturity: v2.0.0
# Date: 2026-01-14

set -euo pipefail
IFS=$'\n\t'

# ============================================================================
# CONFIGURATION
# ============================================================================

BACKUP_DIR="${BACKUP_DIR:-.backups/vaults}"
VAULT_DIR="${VAULT_DIR:-vaults}"
AUDIT_LOG="${AUDIT_LOG:-.audit/rotation/last-validation.log}"

# ============================================================================
# FUNCTIONS
# ============================================================================

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$AUDIT_LOG"
}

fail() {
    log "ERROR: $1"
    exit 1
}

check_backup_exists() {
    log "Phase 1: Checking for existing backups..."
    if [[ ! -d "$BACKUP_DIR" ]] || [[ -z "$(ls -A "$BACKUP_DIR")" ]]; then
        fail "No backups found in $BACKUP_DIR. Rollback path required."
    fi
    log "SUCCESS: Backup verified."
}

check_vault_encrypted() {
    log "Phase 3: Checking for plaintext secrets..."
    local plaintext_files
    plaintext_files=$(grep -rvL "\$ANSIBLE_VAULT;" "$VAULT_DIR"/*.yml 2>/dev/null || true)
    
    if [[ -n "$plaintext_files" ]]; then
        fail "Plaintext detected in vault files: $plaintext_files"
    fi
    log "SUCCESS: All vault files are encrypted."
}

check_inventory_references() {
    log "Phase 4: Checking inventory references..."
    # Verify that vaults mentioned in group_vars exist
    local missing_vaults=0
    for var_file in group_vars/*.yml; do
        if [[ -f "$var_file" ]]; then
            while IFS= read -r line; do
                if [[ "$line" =~ vaults/ ]]; then
                    vault_path=$(echo "$line" | sed "s/.*\(vaults\/[^ '\"$]*\).*/\1/")
                    if [[ ! -f "$vault_path" ]]; then
                        log "WARNING: Inventory references missing vault: $vault_path"
                        missing_vaults=$((missing_vaults + 1))
                    fi
                fi
            done < "$var_file"
        fi
    done
    
    if [[ "$missing_vaults" -gt 0 ]]; then
        fail "Broken symlinks or missing vault references detected."
    fi
    log "SUCCESS: Inventory references validated."
}

# ============================================================================
# EXECUTION (Bauer Verification)
# ============================================================================

mkdir -p "$(dirname "$AUDIT_LOG")"
log "Starting Rotation Readiness Validation (Maturity: v2.0.0)..."

check_backup_exists
check_vault_encrypted
check_inventory_references

log "FINAL STATUS: ROTATION READY."
