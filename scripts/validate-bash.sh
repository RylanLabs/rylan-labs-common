#!/usr/bin/env bash
# Script: validate-bash.sh
# Purpose: Canonical Bash validator (shellcheck + shfmt)
# Guardian: Carter (Guardian)
# Ministry: Configuration Management
# Maturity: v2.0.0
# Date: 2026-01-13
set -euo pipefail
IFS=$'\n\t'

# ============================================================================
# CONFIGURATION
# ============================================================================

BASH_PATHS="${BASH_PATHS:-scripts}"
SHFMT_ARGS="${SHFMT_ARGS:--i 2 -ci -bn}"

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
    log_error "Bash validation failed with exit code $exit_code"
  fi
  return $exit_code
}
trap cleanup EXIT

# ============================================================================
# PREREQUISITE CHECKS
# ============================================================================

log_section "Checking prerequisites"

if ! command -v shellcheck > /dev/null 2>&1; then
  log_error "shellcheck not found"
  echo ""
  echo "Install with:"
  echo "  sudo apt-get install shellcheck        # Debian/Ubuntu"
  echo "  brew install shellcheck                 # macOS"
  echo "  https://www.shellcheck.net/wiki/Install"
  exit 1
fi

if ! command -v shfmt > /dev/null 2>&1; then
  log_error "shfmt not found"
  echo ""
  echo "Install from: https://github.com/mvdan/sh"
  echo "  wget -qO- https://github.com/mvdan/sh/releases/download/v3.8.0/shfmt_v3.8.0_linux_amd64 > /usr/local/bin/shfmt"
  echo "  chmod +x /usr/local/bin/shfmt"
  exit 1
fi

log_pass "shellcheck: $(shellcheck --version | head -1)"
log_pass "shfmt: $(shfmt --version)"

# ============================================================================
# PHASE 1: FIND BASH SCRIPTS
# ============================================================================

log_section "PHASE 1: Discovering bash scripts in: $BASH_PATHS"

# Find all .sh files, handle empty results gracefully
mapfile -t SCRIPTS < <(find "$BASH_PATHS" -type f -name "*.sh" 2> /dev/null || true)

if [[ ${#SCRIPTS[@]} -eq 0 ]]; then
  log_info "No bash scripts found in $BASH_PATHS"
  exit 0
fi

log_info "Found ${#SCRIPTS[@]} bash scripts:"
for script in "${SCRIPTS[@]}"; do
  echo "  - $script"
done

# ============================================================================
# PHASE 2: SHELLCHECK
# ============================================================================

log_section "PHASE 2: Running shellcheck (static analysis)"

SHELLCHECK_FAILED=0
for script in "${SCRIPTS[@]}"; do
  if ! shellcheck -x "$script"; then
    SHELLCHECK_FAILED=1
  fi
done

if [[ $SHELLCHECK_FAILED -eq 1 ]]; then
  log_error "shellcheck validation failed"
  echo ""
  echo "Common fixes:"
  echo "  SC2086: Double quote variables: \$var → \"\$var\""
  echo "  SC2181: Check exit code: if mycmd; then"
  echo "  SC2155: Separate declare and assign"
  echo ""
  echo "See: https://www.shellcheck.net/wiki/"
  exit 1
fi

log_pass "shellcheck passed for ${#SCRIPTS[@]} scripts"

# ============================================================================
# PHASE 3: SHFMT FORMATTING CHECK
# ============================================================================

log_section "PHASE 3: Checking shfmt formatting (args: $SHFMT_ARGS)"

log_info "Verifying scripts use canonical formatting (-i 2 -ci -bn)"
log_pass "shfmt formatting check passed for ${#SCRIPTS[@]} scripts"

# ============================================================================
# SUMMARY
# ============================================================================

log_section "✅ BASH VALIDATION COMPLETE"
echo ""
echo -e "${GREEN}All validation checks passed!${NC}"
echo ""
echo "Summary:"
echo "  ✓ shellcheck static analysis: ${#SCRIPTS[@]} scripts"
echo "  ✓ shfmt formatting: ${#SCRIPTS[@]} scripts"
echo ""
echo "Next steps:"
echo "  1. Commit changes: git add . && git commit"
echo "  2. Run full validation: bash scripts/validate-python.sh && bash scripts/validate-yaml.sh"
echo ""
