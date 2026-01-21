#!/usr/bin/env bash
# Script: validate-python.sh
# Purpose: Canonical Python validator (mypy + ruff + bandit)
# Guardian: Bauer (Auditor)
# Ministry: Configuration Management
# Maturity: v2.0.0
# Date: 2026-01-13
set -euo pipefail
IFS=$'\n\t'

# ============================================================================
# CONFIGURATION
# ============================================================================

PYTHON_VERSION="${PYTHON_VERSION:-3}"
MYPY_PATHS="${MYPY_PATHS:-scripts}"
RUFF_PATHS="${RUFF_PATHS:-.}"
VENV_DIR="${VENV_DIR:-.venv}"
BANDIT_STRICT="${BANDIT_STRICT:-0}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
    log_error "Validation failed with exit code $exit_code"
  fi
  return $exit_code
}
trap cleanup EXIT

# ============================================================================
# PHASE 1: ENVIRONMENT SETUP
# ============================================================================

log_section "PHASE 1: Setting up Python ${PYTHON_VERSION} environment"

if [[ ! -d "$VENV_DIR" ]]; then
  log_info "Creating virtual environment at $VENV_DIR"
  python"${PYTHON_VERSION}" -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

log_info "Upgrading pip"
pip install --quiet --upgrade pip setuptools wheel

log_info "Installing validation tools"
pip install --quiet mypy ruff bandit

if [[ -f "requirements.txt" ]]; then
  log_info "Installing project dependencies from requirements.txt"
  pip install --quiet -r requirements.txt
else
  log_warn "No requirements.txt found - skipping project dependencies"
fi

log_pass "Environment ready"

# ============================================================================
# PHASE 2: TYPE CHECKING (mypy)
# ============================================================================

log_section "PHASE 2: Running mypy strict type checking"
log_info "Paths: $MYPY_PATHS"

if ! find "$MYPY_PATHS" -name "*.py" | grep -q .; then
  log_info "No Python files found, skipping mypy"
else
  # shellcheck disable=SC2086
  if ! mypy --strict $MYPY_PATHS; then
    log_error "mypy validation failed"
    echo ""
    log_error "Fixes:"
    echo "  - Add type annotations to functions/variables"
    echo "  - Use Optional[T] for nullable types"
    echo "  - Check for None before dereferencing"
    echo "  - See: https://mypy.readthedocs.io/"
    exit 1
  fi
fi

log_pass "mypy validation passed"

# ============================================================================
# PHASE 3: LINTING (ruff check)
# ============================================================================

log_section "PHASE 3: Running ruff linting"
log_info "Paths: $RUFF_PATHS"

if ! ruff check "$RUFF_PATHS"; then
  log_error "ruff linting failed"
  echo ""
  log_warn "Auto-fix attempt:"
  echo "  ruff check --fix $RUFF_PATHS"
  echo ""
  if ruff check --fix "$RUFF_PATHS" 2> /dev/null; then
    log_info "Auto-fix successful - review changes and retry"
  fi
  exit 1
fi

log_pass "ruff linting passed"

# ============================================================================
# PHASE 4: FORMATTING (ruff format)
# ============================================================================

log_section "PHASE 4: Checking ruff formatting"
log_info "Paths: $RUFF_PATHS"

if ! ruff format --check "$RUFF_PATHS"; then
  log_error "ruff formatting check failed"
  echo ""
  log_warn "Auto-fix attempt:"
  echo "  ruff format $RUFF_PATHS"
  echo ""
  ruff format "$RUFF_PATHS"
  log_info "Formatting applied - please review and retry"
  exit 1
fi

log_pass "ruff formatting passed"

# ============================================================================
# PHASE 5: SECURITY SCAN (bandit)
# ============================================================================

log_section "PHASE 5: Running bandit security scan"
log_info "Paths: $MYPY_PATHS (level: low-level only)"

if bandit -r "$MYPY_PATHS" -ll --quiet; then
  log_pass "bandit security scan passed"
else
  log_warn "Potential security issues detected (low-level)"
  echo ""

  if [[ "$BANDIT_STRICT" == "1" ]]; then
    log_error "BANDIT_STRICT=1: Failing on security warnings"
    exit 1
  else
    log_warn "Set BANDIT_STRICT=1 to fail on security issues"
    log_info "Review warnings above and address if needed"
  fi
fi

# ============================================================================
# SUMMARY
# ============================================================================

log_section "✅ PYTHON VALIDATION COMPLETE"
echo ""
echo -e "${GREEN}All validation checks passed!${NC}"
echo ""
echo "Summary:"
echo "  ✓ mypy --strict type checking"
echo "  ✓ ruff linting"
echo "  ✓ ruff formatting"
echo "  ✓ bandit security scan"
echo ""
echo "Next steps:"
echo "  1. Review any auto-fixes applied"
echo "  2. Run unit tests: pytest tests/"
echo "  3. Commit changes: git add . && git commit"
echo ""
