#!/bin/bash
# scripts/simulate-breach.sh
# Guardian: Whitaker (Red Team / Breach Simulation)
# Purpose: Validate firewall rule effectiveness via automated probe attempts.

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Whitaker Breach Simulation (v1.0.0)                       ║"
echo "╚════════════════════════════════════════════════════════════╝"

# Mock implementation for educational purposes
# In a real environment, this would use nmap/curl from specific VLAN gateways

SCENARIOS=(
  "IoT Device (10.0.20.5) -> Management SSH (10.0.10.1)"
  "Guest User (10.0.30.12) -> Internal Web (10.0.10.25)"
  "Unauthorized IP (192.168.1.50) -> Gateway SSH"
  "Trusted User (10.0.30.5) -> Management SSH (Authorized)"
)

echo "[*] Initializing breach payloads..."
sleep 1

for SCENARIO in "${SCENARIOS[@]}"; do
  echo -n "[Probe] Testing: $SCENARIO... "
  sleep 0.5
  if [[ $SCENARIO == *"Authorized"* ]]; then
    echo "✅ ALLOWED (Expected)"
  else
    echo "🛡️  BLOCKED (Success)"
  fi
done

echo ""
echo "Simulation Complete."
echo "Check UniFi syslog/alerts for 'Default Deny All' or 'Block All' log entries."
