#!/usr/bin/env bash
# Copyright (c) 2025 Oleksandr Tishchenko / Marketing America Corp
set -euo pipefail

ROOT="${1:-.}"
DOMAIN="${2:-canon}"
DIR="${3:-}"

ROOT="$(cd "$ROOT" && pwd)"

ARGS=(--root "$ROOT" --domain "$DOMAIN")
if [[ -n "$DIR" ]]; then
  ARGS+=(--dir "$DIR")
fi

node "$ROOT/owner/lint/doc-name-check.js" "${ARGS[@]}"
