#!/usr/bin/env bash
set -euo pipefail

# Root runner for Gate
# Usage:
#   ./run.sh .                -> run gate
#   ./run.sh . print          -> run gate, then print proposal (if exists)
#   ./run.sh . safe           -> run gate, then apply SAFE fixes (if proposal exists)
#   ./run.sh . print-safe     -> print + safe apply
# Notes:
# - This script delegates to ./.gate/gate.sh and ./.gate/contract/fix.sh
# - In CI, SAFE apply edits the workspace only; committing is done by agent/bot.

ROOT="${1:-.}"
MODE="${2:-}"

if [[ ! -f "./.gate/gate.sh" ]]; then
  echo "[run] missing ./.gate/gate.sh"
  exit 2
fi

# Ensure executable bits (best-effort)
chmod +x ./.gate/gate.sh 2>/dev/null || true
chmod +x ./.gate/contract/fix.sh 2>/dev/null || true

set +e
./.gate/gate.sh "$ROOT"
RC=$?
set -e

PROPOSAL="./.report/gate-fix-proposal.ndjson"

case "${MODE}" in
  "" )
    exit "$RC"
    ;;
  "print" )
    if [[ -f "$PROPOSAL" ]]; then
      ./.gate/contract/fix.sh "$ROOT" "$PROPOSAL" print || true
    fi
    exit "$RC"
    ;;
  "safe" )
    if [[ -f "$PROPOSAL" ]]; then
      ./.gate/contract/fix.sh "$ROOT" "$PROPOSAL" safe || true
    fi
    exit "$RC"
    ;;
  "print-safe"|"safe-print" )
    if [[ -f "$PROPOSAL" ]]; then
      ./.gate/contract/fix.sh "$ROOT" "$PROPOSAL" print || true
      ./.gate/contract/fix.sh "$ROOT" "$PROPOSAL" safe || true
    fi
    exit "$RC"
    ;;
  * )
    echo "[run] unknown mode: ${MODE}"
    echo "[run] allowed: (empty) | print | safe | print-safe"
    exit 2
    ;;
esac
