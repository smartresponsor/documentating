#!/usr/bin/env bash
set -euo pipefail

zip_path="${1:-}"
if [[ -z "${zip_path}" ]]; then
  echo "usage: archive-flat-root-check.sh <path-to-zip>" >&2
  exit 2
fi
if [[ ! -f "${zip_path}" ]]; then
  echo "ZIP not found: ${zip_path}" >&2
  exit 2
fi

if ! command -v unzip >/dev/null 2>&1; then
  echo "unzip is required for this checker on Unix." >&2
  exit 2
fi

mapfile -t entries < <(unzip -Z1 "${zip_path}" | sed '/^$/d')

declare -A top=()
for e in "${entries[@]}"; do
  e="${e%/}"
  [[ -z "${e}" ]] && continue
  seg="${e%%/*}"
  top["${seg}"]=1
done

count="${#top[@]}"
if [[ "${count}" -eq 1 ]]; then
  for k in "${!top[@]}"; do only="${k}"; break; done
  echo "FAIL: wrapper top folder detected: ${only}. Zip must be flat-root." >&2
  exit 1
fi

echo "OK: flat-root (top-level items: ${count})"
