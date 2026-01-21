#!/usr/bin/env bash
# Script: validate-ansible.sh
# Purpose: Canonical Ansible validator (ansible-lint + syntax check)
# Guardian: Carter (Guardian)
# Ministry: Configuration Management
# Maturity: v2.0.0
# Date: 2026-01-13
set -euo pipefail
IFS=$'\n\t'

# ============================================================================
# CONFIGURATION
# ============================================================================

PLAYBOOK_DIR="${PLAYBOOK_DIR:-playbooks}"
INVENTORY_FILE="${INVENTORY_FILE:-inventory/hosts.yml}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

log_info() {
  echo -e "${BLUE}[INFO]${NC} $*"
}

log_pass() {
  echo -e "${GREEN}[PASS]${NC} $*"
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $*"
}

log_section() {
  echo ""
  echo -e "${BLUE}═══════════════════════════════════════════${NC}"
  echo -e "${BLUE}$*${NC}"
  echo -e "${BLUE}═══════════════════════════════════════════${NC}"
}

# Cleanup trap
cleanup() {
  local exit_code=$?
  if [[ $exit_code -ne 0 ]]; then
    log_error "Ansible validation failed with exit code $exit_code"
  fi
  return $exit_code
}
trap cleanup EXIT

# ============================================================================
# PREREQUISITE CHECKS
# ============================================================================

log_section "Checking prerequisites"

if ! command -v ansible-playbook > /dev/null 2>&1; then
  log_error "ansible-playbook not found"
  echo ""
  echo "Install with:"
  echo "  pip install ansible"
  exit 1
fi

log_pass "ansible-playbook: $(ansible-playbook --version | head -1)"

SKIP_LINT=0
if ! command -v ansible-lint > /dev/null 2>&1; then
  log_warn "ansible-lint not found - skipping linting phase"
  log_info "Install with: pip install ansible-lint"
  SKIP_LINT=1
else
  log_pass "ansible-lint: $(ansible-lint --version)"
fi

# ============================================================================
# PHASE 1: FIND PLAYBOOKS
# ============================================================================

log_section "PHASE 1: Discovering playbooks in: $PLAYBOOK_DIR"

if [[ ! -d "$PLAYBOOK_DIR" ]]; then
  log_info "Playbook directory not found: $PLAYBOOK_DIR"
  log_info "Skipping Ansible validation (no playbooks to validate)"
  exit 0
fi

# Find all playbook files
mapfile -t PLAYBOOKS < <(find "$PLAYBOOK_DIR" -type f \( -name "*.yml" -o -name "*.yaml" \) 2> /dev/null || true)

if [[ ${#PLAYBOOKS[@]} -eq 0 ]]; then
  log_info "No playbooks found in $PLAYBOOK_DIR"
  exit 0
fi

log_info "Found ${#PLAYBOOKS[@]} playbooks:"
for playbook in "${PLAYBOOKS[@]}"; do
  echo "  - $playbook"
done

# ============================================================================
# PHASE 2: ANSIBLE-LINT
# ============================================================================

if [[ "$SKIP_LINT" != "1" ]]; then
  log_section "PHASE 2: Running ansible-lint"

  if ! ansible-lint "$PLAYBOOK_DIR"; then
    log_error "ansible-lint failed"
    echo ""
    echo "Review linting errors above and fix playbooks"
    echo "See: https://ansible-lint.readthedocs.io/"
    exit 1
  fi

  log_pass "ansible-lint validation passed"
else
  log_section "PHASE 2: Skipping ansible-lint (not installed)"
fi

# ============================================================================
# PHASE 3: SYNTAX CHECK
# ============================================================================

log_section "PHASE 3: Running ansible-playbook syntax checks"

SYNTAX_FAILED=0
for playbook in "${PLAYBOOKS[@]}"; do
  log_info "Checking: $playbook"

  # Build ansible-playbook command
  CMD="ansible-playbook --syntax-check"

  # Add inventory if it exists
  if [[ -f "$INVENTORY_FILE" ]]; then
    CMD="$CMD -i $INVENTORY_FILE"
  else
    log_warn "Inventory file not found ($INVENTORY_FILE) - using default"
  fi

  CMD="$CMD $playbook"

  if ! eval "$CMD"; then
    SYNTAX_FAILED=1
    log_error "Syntax check failed: $playbook"
  fi
done

if [[ $SYNTAX_FAILED -eq 1 ]]; then
  log_error "Syntax validation failed for one or more playbooks"
  exit 1
fi

log_pass "Syntax checks passed for ${#PLAYBOOKS[@]} playbooks"

# ============================================================================
# SUMMARY
# ============================================================================

log_section "✅ ANSIBLE VALIDATION COMPLETE"
echo ""
echo -e "${GREEN}All validation checks passed!${NC}"
echo ""
echo "Summary:"
if [[ "$SKIP_LINT" != "1" ]]; then
  echo "  ✓ ansible-lint: ${#PLAYBOOKS[@]} playbooks"
fi
echo "  ✓ Syntax check: ${#PLAYBOOKS[@]} playbooks"
echo ""
echo "Next steps:"
echo "  1. Test playbooks in lab environment: ansible-playbook -i inventory/hosts.yml $PLAYBOOK_DIR/playbook.yml --check"
echo "  2. Commit changes: git add . && git commit"
echo ""
