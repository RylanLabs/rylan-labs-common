#!/usr/bin/env bash
# Script: vault-backup.sh
# Purpose: Create timestamped backups of Ansible Vaults before rotation
# Guardian: Eternal Glue (Resilience)
# Maturity: Level 5 (Autonomous)
# Author: RylanLabs canonical
# Date: 2026-02-05

set -euo pipefail
IFS=$'\n\t'

BACKUP_DIR=".backups/vaults"
VAULT_DIR="vaults"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "[$(date +'%Y-%m-%d %H:%M:%S')] 💾 Eternal Glue: Initializing Vault Backup..."

if [[ ! -d "$VAULT_DIR" ]]; then
    echo "ℹ️ No vault directory found ($VAULT_DIR). Skipping backup."
    exit 0
fi

mkdir -p "$BACKUP_DIR"

# Perform backup
echo "📦 Backing up $VAULT_DIR to $BACKUP_DIR/vault_backup_$TIMESTAMP.tar.gz..."
tar -czf "$BACKUP_DIR/vault_backup_$TIMESTAMP.tar.gz" -C "$VAULT_DIR" .

# Keep only last 5 backups
echo "🧹 Cleaning old backups (Retention: 5)..."
# shellcheck disable=SC2012
ls -t "$BACKUP_DIR"/vault_backup_*.tar.gz 2>/dev/null | tail -n +6 | xargs rm -f || true

echo "✅ Vault backup complete."
exit 0
