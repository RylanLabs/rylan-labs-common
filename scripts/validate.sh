#!/usr/bin/env bash
# Script: validate.sh
# Purpose: Whitaker Compliance Gates - Autonomous Mesh Orchestrator
# Guardian: Bauer (Auditor)
# Ministry: Configuration Management
# Maturity: Level 5 (Autonomous)
# Author: RylanLabs canonical
# Date: 2026-02-04

set -euo pipefail
IFS=$'\n\t'

# ============================================================================
# CONFIGURATION & AUDIT SETUP
# ============================================================================
AUDIT_DIR=".audit"
AUDIT_FILE="${AUDIT_DIR}/validate.json"
EXIT_CODE=0
GATES_RUN=0
SCANNED_RESOURCES=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

mkdir -p "$AUDIT_DIR"

# shellcheck disable=SC2317
error_handler() {
    local line_no=$1
    local exit_code=$2
    if [ "$exit_code" -ne 0 ]; then
        echo -e "${RED}[FAIL]${NC} Compliance Gate failed at line ${line_no} with exit code ${exit_code}"
    fi
}
trap 'error_handler $LINENO $?' ERR

# shellcheck disable=SC2317
cleanup() {
    local status=$?
    if [ "$status" -ne 0 ] && [ "$EXIT_CODE" -eq 0 ]; then EXIT_CODE=$status; fi
    
    # Generate structured Bauer Audit
    cat <<JSON > "$AUDIT_FILE"
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "agent": "Bauer",
  "scanned_repo": "$(basename "$(pwd)")",
  "gates_executed": $GATES_RUN,
  "scanned_resources": $SCANNED_RESOURCES,
  "status": "$([ "$EXIT_CODE" -eq 0 ] && echo "PASS" || echo "FAIL")",
  "exit_code": $EXIT_CODE
}
JSON
    
    if [ "$EXIT_CODE" -ne 0 ]; then
        echo -e "${RED}❌ Bauer: Compliance Validation Failed. See $AUDIT_FILE${NC}"
    else
        echo -e "${GREEN}✅ Bauer: Compliance Validation Passed. All gates green.${NC}"
    fi
    exit "$EXIT_CODE"
}
trap cleanup EXIT

log_gate() { 
    GATES_RUN=$((GATES_RUN + 1))
    echo -e "${BLUE}🛡️  Gate $GATES_RUN: $*...${NC}" 
}

# ============================================================================
# PHASE 1: SOVEREIGN TRINITY GATES
# ============================================================================
log_gate "Whitaker Adversarial Scan"
if [ -f "scripts/whitaker-scan.sh" ]; then
    bash scripts/whitaker-scan.sh || EXIT_CODE=$?
elif [ -f "../rylan-canon-library/scripts/whitaker-scan.sh" ]; then
    bash ../rylan-canon-library/scripts/whitaker-scan.sh || EXIT_CODE=$?
fi

log_gate "Sentinel Expiry Check"
if [ -f "scripts/sentinel-expiry.sh" ]; then
    bash scripts/sentinel-expiry.sh || EXIT_CODE=$?
elif [ -f "../rylan-canon-library/scripts/sentinel-expiry.sh" ]; then
    bash ../rylan-canon-library/scripts/sentinel-expiry.sh || EXIT_CODE=$?
fi

# Exit if primary Trinity gates fail
if [ "$EXIT_CODE" -ne 0 ]; then exit "$EXIT_CODE"; fi

# ============================================================================
# PHASE 2: NO-BYPASS TOOL ENFORCEMENT
# ============================================================================
ensure_tool() {
    local tool=$1
    if ! command -v "$tool" &>/dev/null; then
        echo -e "${RED}❌ Required tool '$tool' is missing.${NC}"
        echo -e "${BLUE}🔧 Attempting autonomous installation...${NC}"
        if command -v apt-get &>/dev/null; then
             sudo apt-get update && sudo apt-get install -y "$tool" || exit 1
        elif command -v brew &>/dev/null; then
             brew install "$tool" || exit 1
        else
             echo "Package manager missing. Install $tool manually."
             exit 1
        fi
    fi
}

# ============================================================================
# PHASE 3: COMPLIANCE GATES (ORCHESTRATION)
# ============================================================================

# 1. Secret Leak Detection
log_gate "Gitleaks (Identity Protection)"
ensure_tool gitleaks
gitleaks detect --source . -v --redact --config .gitleaks.toml || EXIT_CODE=$?

# 2. Dynamic Validator Discovery (Bauer)
# Automatically runs all validate-*.sh scripts in scripts/
while IFS= read -r validator; do
    # Skip self and generic bash validator
    v_base=$(basename "$validator")
    if [[ "$v_base" == "validate.sh" ]] || [[ "$v_base" == "validate-bash.sh" ]]; then continue; fi
    
    log_gate "Running Sub-Validator: $v_base"
    bash "$validator" || EXIT_CODE=$?
    SCANNED_RESOURCES=$((SCANNED_RESOURCES + 1))
done < <(find scripts/ -maxdepth 1 -name "validate-*.sh" || true)

# 3. Mandatory Scaffolding Check (Manifest Driven)
log_gate "Mandatory Scaffolding Verification"
ensure_tool yq
if [ -f "canon-manifest.yaml" ]; then
    # Use cross-version compatible yq filter
    if yq --version 2>&1 | grep -q "yq 0.0.0"; then
        readarray -t REQUIRED_FILES < <(yq -r '.sacred_files[] | .[] | .dest' canon-manifest.yaml || true)
    else
        readarray -t REQUIRED_FILES < <(yq e '.sacred_files[].[] | .dest' canon-manifest.yaml || true)
    fi
    for file in "${REQUIRED_FILES[@]}"; do
        if [[ ! -f "$file" && ! -d "$file" ]]; then
            echo -e "${RED}❌ Missing mandatory artifact: $file${NC}"
            EXIT_CODE=1
        else
            SCANNED_RESOURCES=$((SCANNED_RESOURCES + 1))
        fi
    done
else
    # Fallback to local hardcoded defaults
    DEFAULTS=(Makefile .gitleaks.toml README.md common.mk .sops.yaml)
    for f in "${DEFAULTS[@]}"; do
        [[ ! -f "$f" ]] && { echo -e "${RED}❌ Missing: $f${NC}"; EXIT_CODE=1; }
    done
fi

# 4. Bash Logic & Structure (ShellCheck) - Run Last
log_gate "ShellCheck Static Analysis"
ensure_tool shellcheck
# Scans existing script directories
SCAN_PATHS=()
[[ -d "scripts" ]] && SCAN_PATHS+=("scripts")
[[ -d "patterns" ]] && SCAN_PATHS+=("patterns")

if [ ${#SCAN_PATHS[@]} -gt 0 ]; then
    find "${SCAN_PATHS[@]}" -name "*.sh" -exec shellcheck -x {} + || EXIT_CODE=$?
fi

exit "$EXIT_CODE"
