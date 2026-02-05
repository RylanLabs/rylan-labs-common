#!/usr/bin/env bash
# Script: validate-sops.sh
# Purpose: ML5 Autonomous SOPS Validator (Verify, Audit, Remediate)
# Agent: Beale (Hardening)
# Author: RylanLabs canonical
# Date: 2026-02-04
# Maturity: Level 5 (Autonomous)

set -euo pipefail
IFS=$'\n\t'

# ============================================================================
# CONFIGURATION
# ============================================================================
AUDIT_DIR=".audit"
AUDIT_FILE="${AUDIT_DIR}/validate-sops.json"
SOPS_CONFIG=".sops.yaml"
FIX_MODE=false
EXIT_CODE=0
SCANNED_COUNT=0
FAILED_COUNT=0

# Files to EXPLICITLY ignore because they are known infrastructure/config
IGNORE_REGEX="(\.sops\.yaml$|\.github/.*|node_modules/.*|\.git/.*|common\.mk$|README\.md$)"

mkdir -p "$AUDIT_DIR"

# shellcheck disable=SC2317
cleanup() {
    local status=$?
    if [ "$status" -ne 0 ] && [ "$EXIT_CODE" -eq 0 ]; then EXIT_CODE=$status; fi
    echo "{\"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"agent\": \"Beale\", \"scanned\": \"$SCANNED_COUNT\", \"failed\": \"$FAILED_COUNT\", \"exit_code\": \"$EXIT_CODE\"}" > "$AUDIT_FILE"
    if [ "$EXIT_CODE" -ne 0 ]; then echo "❌ Beale: SOPS Validation Failed."; else echo "✅ Beale: SOPS Validation Passed ($SCANNED_COUNT files checked)."; fi
    exit "$EXIT_CODE"
}
trap cleanup EXIT

while [[ $# -gt 0 ]]; do
    case "$1" in
        --fix) FIX_MODE=true; shift ;;
        *) echo "Unknown argument: $1"; exit 1 ;;
    esac
done

# ============================================================================
# PATTERN DISCOVERY
# ============================================================================
DEFAULT_PATTERNS=("vault_.*\.ya?ml$" "secrets_.*\.ya?ml$" ".*secret.*\.ya?ml$" "vaults/.*\.ya?ml$")
PATTERNS=()

if [ -f "$SOPS_CONFIG" ] && command -v yq &> /dev/null; then
    if yq e '.creation_rules[].path_regex' "$SOPS_CONFIG" &>/dev/null; then
        readarray -t PATTERNS < <(yq e '.creation_rules[].path_regex' "$SOPS_CONFIG" | sed 's/\*/.*/g')
    elif yq -r '.creation_rules[].path_regex' "$SOPS_CONFIG" &>/dev/null; then
        readarray -t PATTERNS < <(yq -r '.creation_rules[].path_regex' "$SOPS_CONFIG" | sed 's/\*/.*/g')
    fi
fi

if [ ${#PATTERNS[@]} -eq 0 ]; then PATTERNS=("${DEFAULT_PATTERNS[@]}"); fi

# ============================================================================
# VALIDATION ENGINE
# ============================================================================
HAS_SOPS=$(command -v sops &> /dev/null && echo true || echo false)
readarray -t UNIQUE_PATTERNS < <(printf "%s\n" "${PATTERNS[@]}" | sort -u)

for pattern in "${UNIQUE_PATTERNS[@]}"; do
    while IFS= read -r -d '' FILE; do
        [[ -e "$FILE" ]] || continue
        if [[ "$FILE" =~ $IGNORE_REGEX ]]; then continue; fi
        
        SCANNED_COUNT=$((SCANNED_COUNT + 1))
        IS_ENCRYPTED=false
        
        # 1. Cryptographic Verification
        if [ "$HAS_SOPS" = true ]; then
            if sops --verify "$FILE" &> /dev/null; then
                IS_ENCRYPTED=true
            fi
        fi
        
        # 2. Heuristic Marker Check (Fallback)
        if [ "$IS_ENCRYPTED" = false ]; then
            if grep -q "sops" "$FILE" && grep -q "ENC\[AES256_GCM" "$FILE"; then
                IS_ENCRYPTED=true
            elif grep -q "ANSIBLE_VAULT" "$FILE"; then
                IS_ENCRYPTED=true
            fi
        fi
        
        if [ "$IS_ENCRYPTED" = false ]; then
            echo "❌ LEAK DETECTED: $FILE"
            FAILED_COUNT=$((FAILED_COUNT + 1))
            EXIT_CODE=1
            if [ "$FIX_MODE" = true ] && [ "$HAS_SOPS" = true ]; then
                echo "🩹 Lazarus: Attempting to encrypt $FILE..."
                if sops -e -i "$FILE" &>/dev/null; then 
                    echo "✅ Encrypted: $FILE"
                    FAILED_COUNT=$((FAILED_COUNT - 1))
                else
                    echo "❌ Failed to encrypt: $FILE"
                fi
            fi
        fi
    done < <(find . -maxdepth 10 -regextype posix-extended -regex ".*/${pattern}" -not -path "*/.git/*" -print0)
done

[ $FAILED_COUNT -eq 0 ] && [ $EXIT_CODE -eq 1 ] && EXIT_CODE=0
exit $EXIT_CODE
