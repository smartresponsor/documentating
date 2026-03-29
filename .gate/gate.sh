#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-$(pwd)}"
QUALITY="${QUALITY:-0}"

# Proposal path (relative to repo root)
PROPOSAL_PATH="${GATE_PROPOSAL_FILE:-.report/gate-fix-proposal.ndjson}"

is_ci() {
  [[ "${GITHUB_ACTIONS:-}" == "true" ]] && return 0
  [[ "${CI:-}" == "true" ]] && return 0
  return 1
}

AUTO_FIX_SAFE="${AUTO_FIX_SAFE:-}"
if [[ -z "$AUTO_FIX_SAFE" ]]; then
  if is_ci; then AUTO_FIX_SAFE="0"; else AUTO_FIX_SAFE="1"; fi
fi

# Normalize root + run from repo root
REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"
cd "$REPO_ROOT"

fail_step=""
fail_code=0

run_step() {
  local name="$1"; shift
  if [[ -n "$fail_step" ]]; then
    return 0
  fi

  set +e
  "$@"
  local code=$?
  set -e

  if [[ "$code" != "0" ]]; then
    fail_step="$name"
    fail_code="$code"
  fi
  return 0
}

print_proposal() {
  if [[ -f "$PROPOSAL_PATH" ]]; then
    echo "[gate] proposal file: $PROPOSAL_PATH"
    echo "[gate] proposal entries:"
    cat "$PROPOSAL_PATH" || true
  fi
}

apply_safe_if_local() {
  # only on local runs
  [[ "$AUTO_FIX_SAFE" == "1" ]] || return 0
  # only if failed
  [[ -n "$fail_step" ]] || return 0
  # avoid recursion
  [[ "${_GATE_AUTOFIX_RERUN:-0}" != "1" ]] || return 0
  # only if proposal exists
  [[ -f "$PROPOSAL_PATH" ]] || return 0

  echo "[gate] local autofix-safe enabled: applying proposals..."
  chmod +x ".gate/contract/fix.sh" 2>/dev/null || true
  ".gate/contract/fix.sh" "." "$PROPOSAL_PATH" safe || true

  echo "[gate] re-running gate after autofix-safe..."
  AUTO_FIX_SAFE="0" _GATE_AUTOFIX_RERUN="1" bash ".gate/gate.sh" "."
  exit $?
}

echo "[gate] repo=${GITHUB_REPOSITORY:-local} mode=${GATE_MODE:-unknown} root=$REPO_ROOT"

# Contract
run_step "root-contract-check" bash ".gate/contract/sh/root-contract-check.sh" "$REPO_ROOT"
run_step "gitignore-template-check" bash ".gate/contract/sh/gitignore-template-check.sh" "$REPO_ROOT"

# Linting (fast checks) - JS checks require node
if command -v node >/dev/null 2>&1; then
  run_step "no-plural-check" node ".gate/linting/js/no-plural-check.js" "$REPO_ROOT"
  run_step "layer-mirror-check-js" node ".gate/linting/js/layer-mirror-check.js" "$REPO_ROOT"
  run_step "doc-name-check-js" node ".gate/linting/js/doc-name-check.js" "$REPO_ROOT"
  run_step "archive-name-check-js" node ".gate/linting/js/archive-name-check.js" "$REPO_ROOT"
else
  echo "[gate] node not found, skipping JS linting checks"
fi

run_step "copyright-header-check" bash ".gate/linting/sh/copyright-header-check.sh" "$REPO_ROOT"
run_step "layer-mirror-check-sh" bash ".gate/linting/sh/layer-mirror-check.sh" "$REPO_ROOT"
run_step "doc-name-check-sh" bash ".gate/linting/sh/doc-name-check.sh" "$REPO_ROOT"
run_step "archive-flat-root-check" bash ".gate/linting/sh/archive-flat-root-check.sh" "$REPO_ROOT"

if [[ "$QUALITY" == "1" ]]; then
  run_step "quality-run" bash ".gate/quality/sh/quality-run.sh" "$REPO_ROOT"
fi

if [[ -n "$fail_step" ]]; then
  echo "[gate] FAIL step=$fail_step code=$fail_code"
  print_proposal
  apply_safe_if_local
  exit "$fail_code"
fi

echo "Gate OK"
