#!/usr/bin/env bash
# Script: validate-yaml.sh
# Purpose: Canonical YAML validator (yamllint)
# Guardian: Bauer (Auditor)
# Ministry: Configuration Management
# Maturity: v2.0.0
# Date: 2026-01-13
set -euo pipefail
IFS=$'\n\t'

# ============================================================================
# CONFIGURATION
# ============================================================================

YAML_PATHS="${YAML_PATHS:-.}"
YAMLLINT_CONFIG="${YAMLLINT_CONFIG:-configs/.yamllint}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
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
    log_error "YAML validation failed with exit code $exit_code"
  fi
  return $exit_code
}
trap cleanup EXIT

# ============================================================================
# PREREQUISITE CHECKS
# ============================================================================

log_section "Checking prerequisites"

if ! command -v yamllint > /dev/null 2>&1; then
  log_error "yamllint not found"
  echo ""
  echo "Install with:"
  echo "  pip install yamllint"
  exit 1
fi

log_pass "yamllint: $(yamllint --version)"

# ============================================================================
# PHASE 1: VALIDATE CONFIG FILE
# ============================================================================

log_section "PHASE 1: Validating yamllint configuration"

if [[ ! -f "$YAMLLINT_CONFIG" ]]; then
  log_error "yamllint config not found: $YAMLLINT_CONFIG"
  echo ""
  echo "Create $YAMLLINT_CONFIG or set YAMLLINT_CONFIG environment variable"
  echo ""
  echo "Example: configs/.yamllint"
  exit 1
fi

log_info "Using config: $YAMLLINT_CONFIG"
log_pass "Config file exists and readable"

# ============================================================================
# PHASE 2: RUN YAMLLINT
# ============================================================================

log_section "PHASE 2: Running yamllint"
log_info "Paths: $YAML_PATHS"

if ! yamllint -c "$YAMLLINT_CONFIG" "$YAML_PATHS"; then
  log_error "yamllint validation failed"
  echo ""
  echo "Common fixes:"
  echo "  indentation: Use 2-space indent, not 4 or tabs"
  echo "  line-length: Keep lines under 120 chars (140 for inventory)"
  echo "  trailing-spaces: Remove whitespace at line end"
  echo "  comments: Ensure 2 spaces before inline comments"
  echo ""
  echo "Auto-fix (manual review required):"
  echo "  # Fix indentation manually or use sed"
  echo ""
  echo "See: https://yamllint.readthedocs.io/"
  exit 1
fi

log_pass "yamllint validation passed"

# ============================================================================
# SUMMARY
# ============================================================================

log_section "✅ YAML VALIDATION COMPLETE"
echo ""
echo -e "${GREEN}All validation checks passed!${NC}"
echo ""
echo "Summary:"
echo "  ✓ yamllint: Config files valid"
echo "  ✓ yamllint: Syntax and style OK"
echo ""
echo "Next steps:"
echo "  1. Commit changes: git add . && git commit"
echo "  2. Run full validation: bash scripts/validate-python.sh && bash scripts/validate-bash.sh"
echo ""
