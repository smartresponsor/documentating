#!/usr/bin/env bash
set -euo pipefail

# Create patch artifacts under .commanding/patch/
# Output: .commanding/patch/patch.diff and patch.zip

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
OUT_DIR="$ROOT/.commanding/patch"
mkdir -p "$OUT_DIR"

DIFF_FILE="$OUT_DIR/patch.diff"
ZIP_FILE="$OUT_DIR/patch.zip"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git diff >"$DIFF_FILE"
else
  echo 'Not a git repo; patch.diff will be empty.' >"$DIFF_FILE"
fi

( cd "$OUT_DIR" && zip -q -9 -r "${ZIP_FILE}" "patch.diff" )

echo "OK: $DIFF_FILE"
echo "OK: $ZIP_FILE"
