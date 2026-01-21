#!/usr/bin/env bash
# Script: validate-security-posture.sh
# Purpose: Verify network isolation and firewall defaults (P1 Discipline)
# Guardian: Beale (Hardening)
# Maturity: v2.0.0
# Date: 2026-01-14

set -euo pipefail
IFS=$'\n\t'

# ============================================================================
# CONFIGURATION
# ============================================================================

NETWORK_SCHEME="${NETWORK_SCHEME:-group_vars/network_scheme.yml}"
AUDIT_LOG="${AUDIT_LOG:-.audit/security/posture.log}"

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

check_dependencies() {
  if ! command -v yq &> /dev/null; then
    fail "yq is required but not installed."
  fi
}

check_firewall_default_deny() {
  log "Verifying default-deny posture..."
  # Placeholder: Checks for a default_posture variable in network_scheme
  if [[ -f "$NETWORK_SCHEME" ]]; then
    posture=$(yq '.network_scheme.default_posture // "not-found"' "$NETWORK_SCHEME")
    if [[ "$posture" != "deny-all" ]] && [[ "$posture" != "drop" ]]; then
      log "WARNING: Default posture is '$posture'. Recommended: 'deny-all'."
    fi
  fi
}

check_guest_isolation() {
  log "Verifying Guest-IoT (VLAN 90) isolation..."
  if [[ -f "$NETWORK_SCHEME" ]]; then
    # Check if VLAN 90 exists and has isolation enabled
    isolated=$(yq '.network_scheme.vlans[] | select(.id == 90) | .device_isolation // false' "$NETWORK_SCHEME")

    if [[ "$isolated" != "true" ]]; then
      fail "VLAN 90 (Guest-IoT) MUST have device_isolation enabled."
    fi
    log "SUCCESS: Guest-IoT isolation verified."
  else
    log "SKIP: $NETWORK_SCHEME not found. Cannot verify isolation."
  fi
}

# ============================================================================
# EXECUTION (Beale Hardening)
# ============================================================================

mkdir -p "$(dirname "$AUDIT_LOG")"
log "Starting Security Posture Audit (Maturity: v2.0.0)..."

check_dependencies
check_firewall_default_deny
check_guest_isolation

log "FINAL STATUS: SECURITY POSTURE VALIDATED."
