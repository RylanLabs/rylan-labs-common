#!/usr/bin/env bash
# Script: sync-vault-secrets.sh
# Purpose: Sync secrets from rylanlabs-private-vault to GitHub
# Domain: Audit (Verification)
# Compliance: Seven Pillars ✓ | 3-Domain ✓ | Production Standards ✓
# Author: RylanLabs CI/CD
# Date: 2025-12-29

set -euo pipefail
IFS=$'\n\t'

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

log_pass() {
  echo -e "${GREEN}[PASS]${NC} $1"
}

log_fail() {
  echo -e "${RED}[FAIL]${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

# Validate environment
validate_env() {
  log_info "Validating environment..."

  # Check required tools
  for cmd in gh git ssh-keyscan; do
    command -v "$cmd" > /dev/null 2>&1 || (
      log_fail "$cmd not found"
      exit 1
    )
  done

  # Check GitHub token
  if [ -z "${GITHUB_TOKEN:-}" ]; then
    log_fail "GITHUB_TOKEN not set"
    exit 1
  fi

  log_pass "Environment validated"
}

# Clone vault repository
clone_vault() {
  log_info "Cloning rylanlabs-private-vault..."

  VAULT_DIR="/tmp/rylanlabs-private-vault-$$"
  mkdir -p "$VAULT_DIR"

  # Add GitHub SSH key to known_hosts
  ssh-keyscan -H github.com >> ~/.ssh/known_hosts 2> /dev/null

  # Clone with SSH (requires SSH key in secrets)
  git clone git@github.com:RylanLabs/rylanlabs-private-vault.git "$VAULT_DIR" 2> /dev/null || {
    log_fail "Failed to clone vault. Ensure VAULT_SSH_KEY is set in GitHub Secrets"
    return 1
  }

  log_pass "Vault cloned to $VAULT_DIR"
  echo "$VAULT_DIR"
}

# Read API key from vault
read_api_key() {
  local vault_dir="$1"
  local api_key_file="${vault_dir}/keys/ansible-galaxy/api-key.txt"

  log_info "Reading GALAXY_API_KEY from vault..."

  if [ ! -f "$api_key_file" ]; then
    log_fail "API key file not found: $api_key_file"
    return 1
  fi

  API_KEY=$(tr -d '\n' < "$api_key_file")

  # Verify it's not empty and looks like a token
  if [ -z "$API_KEY" ] || [ ${#API_KEY} -lt 10 ]; then
    log_fail "API key invalid (too short or empty)"
    return 1
  fi

  log_pass "API key read (${#API_KEY} chars)"
  echo "$API_KEY"
}

# Update GitHub Secret
update_github_secret() {
  local secret_name="$1"
  local secret_value="$2"

  log_info "Updating GitHub Secret: $secret_name..."

  # Use gh CLI to set secret
  echo "$secret_value" | gh secret set "$secret_name" --repo "$GITHUB_REPOSITORY" || {
    log_fail "Failed to update secret"
    return 1
  }

  log_pass "GitHub Secret updated: $secret_name"
}

# Verify secret sync
verify_secret() {
  local secret_name="$1"

  log_info "Verifying secret sync..."

  # Check if secret exists (gh doesn't return the value, just verifies it exists)
  gh secret list --repo "$GITHUB_REPOSITORY" | grep -q "^$secret_name" || {
    log_fail "Secret not found after sync"
    return 1
  }

  log_pass "Secret verified: $secret_name"
}

# Create audit log
create_audit_log() {
  local secret_name="$1"

  log_info "Creating audit log..."

  mkdir -p .audit/vault-syncs

  cat > ".audit/vault-syncs/sync-$(date +%s).json" << EOF
    {
      "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
      "run_id": "${GITHUB_RUN_ID:-local}",
      "workflow": "security-scan",
      "secret_name": "$secret_name",
      "repository": "${GITHUB_REPOSITORY:-local}",
      "actor": "${GITHUB_ACTOR:-local}",
      "status": "success"
    }
EOF

  log_pass "Audit log created"
}

# Cleanup
cleanup() {
  if [ -n "${VAULT_DIR:-}" ] && [ -d "$VAULT_DIR" ]; then
    log_info "Cleaning up temporary vault directory..."
    rm -rf "$VAULT_DIR"
    log_pass "Cleanup complete"
  fi
}

trap cleanup EXIT

# Main execution
main() {
  log_info "=== RylanLabs Vault Secrets Sync ==="
  echo ""

  validate_env

  VAULT_DIR=$(clone_vault) || exit 1

  API_KEY=$(read_api_key "$VAULT_DIR") || exit 1

  update_github_secret "GALAXY_API_KEY" "$API_KEY" || exit 1

  verify_secret "GALAXY_API_KEY" || exit 1

  create_audit_log "GALAXY_API_KEY"

  echo ""
  log_pass "=== Vault sync complete ==="
}

main "$@"
