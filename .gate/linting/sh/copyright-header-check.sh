#!/usr/bin/env bash
# Copyright (c) 2025 Oleksandr Tishchenko / Marketing America Corp
set -euo pipefail

ROOT="${1:-.}"
ROOT="$(cd "$ROOT" && pwd)"

HEADER='Copyright (c) 2025 Oleksandr Tishchenko / Marketing America Corp'

IGNORE_DIR=(.git node_modules vendor var build dist .idea .vscode cache fixture)
EXT=(php js ts tsx sh ps1)

is_ignored() {
  local p="$1"
  for d in "${IGNORE_DIR[@]}"; do
    case "$p" in
      *"/$d/"*) return 0 ;;
    esac
  done
  return 1
}

has_ext() {
  local f="$1"
  for e in "${EXT[@]}"; do
    if [[ "$f" == *".$e" ]]; then
      return 0
    fi
  done
  return 1
}

bad=0
while IFS= read -r -d '' f; do
  rel="${f#$ROOT/}"
  if is_ignored "/$rel/"; then
    continue
  fi
  if ! has_ext "$f"; then
    continue
  fi
  head_txt="$(head -n 12 "$f" 2>/dev/null || true)"
  if [[ "$head_txt" != *"$HEADER"* ]]; then
    echo "missing header: $rel"
    bad=$((bad+1))
  fi

done < <(find "$ROOT" -type f -print0)

if [[ $bad -gt 0 ]]; then
  echo "FAIL: $bad file(s) missing copyright header." >&2
  exit 2
fi

echo "OK: header present."
