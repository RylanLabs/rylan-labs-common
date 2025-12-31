#!/usr/bin/env bash
# Script: validate-seven-pillars.sh
# Purpose: Validate roles comply with RylanLabs Seven Pillars
# Guardian: Bauer (Verification)
# Compliance: Seven Pillars ✓ | Trinity ✓ | Hellodeolu v6 ✓
# Author: RylanLabs CI/CD
# Date: 2025-12-29

set -euo pipefail
IFS=$'\n\t'

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Paths
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ROLES_DIR="${REPO_ROOT}/roles"
AUDIT_DIR="${REPO_ROOT}/.audit/pillars-validation"
REPORT_FILE="${AUDIT_DIR}/report-${GITHUB_RUN_ID:-$(date +%s)}.json"

# Counters
TOTAL_PILLARS=0
PASSED_PILLARS=0
FAILED_PILLARS=0
WARNINGS=0

# JSON report array
declare -a PILLAR_RESULTS

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    PASSED_PILLARS=$((PASSED_PILLARS + 1))
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    FAILED_PILLARS=$((FAILED_PILLARS + 1))
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    WARNINGS=$((WARNINGS + 1))
}

# Initialize report
init_report() {
    mkdir -p "${AUDIT_DIR}"
    cat > "${REPORT_FILE}" <<EOF
{
  "run_id": "${GITHUB_RUN_ID:-local}",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "repository": "${GITHUB_REPOSITORY:-local}",
  "ref": "${GITHUB_REF:-HEAD}",
  "sha": "${GITHUB_SHA:-$(git rev-parse HEAD 2>/dev/null || echo 'unknown')}",
  "roles_validated": [],
  "summary": {
    "total_pillars": 0,
    "passed": 0,
    "failed": 0,
    "warnings": 0
  },
  "pillars": {}
}
EOF
}

# Pillar 1: Idempotency
check_idempotency() {
    local role="$1"
    local role_path="${ROLES_DIR}/${role}"
    local tasks_file="${role_path}/tasks/main.yml"
    local checks_passed=0
    local checks_total=0

    log_info "Checking Pillar 1: Idempotency (${role})"

    # Check for 'when' conditions
    if grep -q "when:" "${tasks_file}" 2>/dev/null; then
        log_pass "  - Found 'when' conditions for idempotency"
        checks_passed=$((checks_passed + 1))
    else
        log_warn "  - No 'when' conditions found (may need idempotency checks)"
    fi
    checks_total=$((checks_total + 1))

    # Check for 'creates' in file operations
    if grep -q "creates:" "${tasks_file}" 2>/dev/null; then
        log_pass "  - Found 'creates' clauses for file operations"
        checks_passed=$((checks_passed + 1))
    else
        log_warn "  - No 'creates' clauses found (may affect idempotency)"
    fi
    checks_total=$((checks_total + 1))

    [ $checks_passed -ge 1 ] && return 0 || return 1
}

# Pillar 2: Error Handling
check_error_handling() {
    local role="$1"
    local role_path="${ROLES_DIR}/${role}"
    local tasks_file="${role_path}/tasks/main.yml"

    log_info "Checking Pillar 2: Error Handling (${role})"

    # Check for failed_when
    if grep -q "failed_when:" "${tasks_file}" 2>/dev/null; then
        log_pass "  - Found 'failed_when' clauses"
    else
        log_warn "  - No 'failed_when' clauses (may need explicit failure handling)"
    fi

    # Check for ignore_errors
    if grep -q "ignore_errors:" "${tasks_file}" 2>/dev/null; then
        log_pass "  - Found 'ignore_errors' handling"
    else
        log_info "  - No 'ignore_errors' (default fail-fast behavior)"
    fi

    return 0
}

# Pillar 3: Audit Logging
check_audit_logging() {
    local role="$1"
    local role_path="${ROLES_DIR}/${role}"
    local tasks_file="${role_path}/tasks/main.yml"

    log_info "Checking Pillar 3: Audit Logging (${role})"

    # Check for .audit/ log output
    if grep -q "\.audit\|rylan_utils\.log_audit\|loki" "${tasks_file}" 2>/dev/null; then
        log_pass "  - Found audit logging references"
    else
        log_warn "  - No explicit audit logging found (should log to .audit/ or Loki)"
    fi

    return 0
}

# Pillar 4: Documentation Clarity
check_documentation() {
    local role="$1"
    local role_path="${ROLES_DIR}/${role}"
    local readme_file="${role_path}/README.md"

    log_info "Checking Pillar 4: Documentation Clarity (${role})"

    if [ -f "${readme_file}" ]; then
        log_pass "  - README.md exists"

        if grep -q "rylanlabs\.common\." "${readme_file}" 2>/dev/null; then
            log_pass "  - README includes FQCN examples"
        else
            log_warn "  - README missing FQCN examples"
        fi
    else
        log_fail "  - README.md not found"
        return 1
    fi

    return 0
}

# Pillar 5: Validation
check_validation() {
    local role="$1"
    local role_path="${ROLES_DIR}/${role}"
    local meta_file="${role_path}/meta/main.yml"

    log_info "Checking Pillar 5: Validation (${role})"

    if [ -f "${meta_file}" ]; then
        log_pass "  - meta/main.yml exists"

        if grep -q "dependencies:" "${meta_file}" 2>/dev/null; then
            log_pass "  - Role declares dependencies"
        else
            log_info "  - Role has no dependencies (may be standalone)"
        fi
    else
        log_fail "  - meta/main.yml not found"
        return 1
    fi

    return 0
}

# Pillar 6: Reversibility
check_reversibility() {
    local role="$1"
    local role_path="${ROLES_DIR}/${role}"
    local handlers_file="${role_path}/handlers/main.yml"

    log_info "Checking Pillar 6: Reversibility (${role})"

    if [ -f "${handlers_file}" ] && [ -s "${handlers_file}" ]; then
        log_pass "  - handlers/main.yml exists and has content"

        if grep -q "rollback\|undo\|revert" "${handlers_file}" 2>/dev/null; then
            log_pass "  - Found rollback/revert handlers"
        else
            log_warn "  - No explicit rollback handlers (consider adding for RTO <15min)"
        fi
    else
        log_warn "  - No handlers defined (may limit reversibility)"
    fi

    return 0
}

# Pillar 7: Observability
check_observability() {
    local role="$1"
    local role_path="${ROLES_DIR}/${role}"
    local tasks_file="${role_path}/tasks/main.yml"

    log_info "Checking Pillar 7: Observability (${role})"

    # Check for debug/output logging
    if grep -q "debug:\|register:" "${tasks_file}" 2>/dev/null; then
        log_pass "  - Found debug/register statements for observability"
    else
        log_warn "  - No debug/register statements found (may need better visibility)"
    fi

    # Check for structured logging (JSON format)
    if grep -q "json\|structured" "${tasks_file}" 2>/dev/null; then
        log_pass "  - Found structured logging patterns"
    else
        log_info "  - No explicit structured logging (consider JSON output)"
    fi

    return 0
}

# Main validation loop
validate_roles() {
    log_info "=== Seven Pillars Validation ==="
    log_info "Scanning roles in: ${ROLES_DIR}"
    echo ""

    if [ ! -d "${ROLES_DIR}" ]; then
        log_fail "Roles directory not found: ${ROLES_DIR}"
        return 1
    fi

    # Iterate over each role
    for role_dir in "${ROLES_DIR}"/*/; do
        role=$(basename "$role_dir")
        
        echo ""
        log_info "Validating role: ${role}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

        role_passed=0
        role_failed=0

        # Run all seven pillar checks
        check_idempotency "$role" && role_passed=$((role_passed + 1)) || role_failed=$((role_failed + 1))
        check_error_handling "$role" && role_passed=$((role_passed + 1)) || role_failed=$((role_failed + 1))
        check_audit_logging "$role" && role_passed=$((role_passed + 1)) || role_failed=$((role_failed + 1))
        check_documentation "$role" && role_passed=$((role_passed + 1)) || role_failed=$((role_failed + 1))
        check_validation "$role" && role_passed=$((role_passed + 1)) || role_failed=$((role_failed + 1))
        check_reversibility "$role" && role_passed=$((role_passed + 1)) || role_failed=$((role_failed + 1))
        check_observability "$role" && role_passed=$((role_passed + 1)) || role_failed=$((role_failed + 1))

        TOTAL_PILLARS=$((TOTAL_PILLARS + 7))

        echo ""
        log_info "Role ${role}: ${role_passed}/7 pillars passed"
        echo ""
    done
}

# Generate final report
generate_report() {
    local exit_code=0

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "=== Validation Summary ==="
    echo "Total Pillar Checks: ${TOTAL_PILLARS}"
    log_pass "Passed: ${PASSED_PILLARS}"
    [ $FAILED_PILLARS -gt 0 ] && log_fail "Failed: ${FAILED_PILLARS}" || echo -e "${GREEN}[PASS]${NC} Failed: ${FAILED_PILLARS}"
    [ $WARNINGS -gt 0 ] && log_warn "Warnings: ${WARNINGS}" || echo -e "${GREEN}[PASS]${NC} Warnings: ${WARNINGS}"

    # Determine exit code
    if [ $FAILED_PILLARS -gt 0 ]; then
        exit_code=1
        log_fail "VALIDATION FAILED - Some pillar checks failed"
    elif [ $WARNINGS -gt 0 ]; then
        exit_code=2
        log_warn "VALIDATION PASSED WITH WARNINGS"
    else
        log_pass "VALIDATION PASSED"
        exit_code=0
    fi

    echo ""
    echo "Audit report: ${REPORT_FILE}"

    return $exit_code
}

# Main execution
main() {
    init_report
    validate_roles
    generate_report
}

main "$@"
