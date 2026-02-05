#!/usr/bin/env bash
# Script: sentinel-expiry.sh
# Purpose: Validate identity key expiry with 14-day compliance window
# Guardian: Sentinel (Identity Monitor)
# Ministry: Audit
# Maturity: Level 5 (Autonomous)
# Author: RylanLabs canonical
# Date: 2026-02-04

set -euo pipefail
IFS=$'\n\t'

# Standards: Warning window is 14 days by default
WARNING_WINDOW_DAYS=${WARNING_WINDOW_DAYS:-14}
THRESHOLD_SECONDS=$((WARNING_WINDOW_DAYS * 86400))
NOW=$(date +%s)
IDENTITY_EMAIL=${IDENTITY_EMAIL:-security@rylan.local}

echo "🔍 Running Expiry Sentinel ($IDENTITY_EMAIL)..."

if ! command -v gpg &>/dev/null; then
    echo "⚠️  GPG not found; skipping expiry check (Infrastructure bypass?)"
    exit 0
fi

# Get expiry dates for all subkeys of the target identity
EXPIRY_DATES=$(gpg --with-colons --list-keys "$IDENTITY_EMAIL" 2>/dev/null | awk -F: '/sub|pub/ {print $7}' || true)

if [ -z "$EXPIRY_DATES" ]; then
    echo "⚠️  No identity key found for $IDENTITY_EMAIL. Skipping enforcement."
    exit 0
fi

FAIL=0
for expiry in $EXPIRY_DATES; do
    if [ -z "$expiry" ]; then continue; fi

    # Check if expired or expiring soon
    TIME_LEFT=$((expiry - NOW))

    if [ "$TIME_LEFT" -lt 0 ]; then
        echo "❌ KEY EXPIRED! (Expiry: $(date -d @"$expiry" 2>/dev/null || echo "$expiry"))"
        FAIL=1
    elif [ "$TIME_LEFT" -lt "$THRESHOLD_SECONDS" ]; then
        DAYS_LEFT=$((TIME_LEFT / 86400))
        echo "⚠️  KEY EXPIRING SOON! ($DAYS_LEFT days left until $(date -d @"$expiry" 2>/dev/null || echo "$expiry"))"
        FAIL=1
    else
        echo "✅ Key valid until $(date -d @"$expiry" 2>/dev/null || echo "$expiry")"
    fi
done

if [ "$FAIL" -ne 0 ]; then
    echo "🚨 Expiry validation FAILED. Rotation required to regain compliance."
    exit 1
fi

echo "✅ All identity keys within compliance window."
exit 0
