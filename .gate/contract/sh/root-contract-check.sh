#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-.}"
REPO_ROOT="${REPO_ROOT%/}"

fail=0
issues=()

required_files=(".gitignore" "MANIFEST.json" "README.md")
allowed_files=(".gitignore" "MANIFEST.json" "README.md" ".gitattributes")

is_allowed_root_file() {
  local name="$1"
  for f in "${allowed_files[@]}"; do
    if [[ "$name" == "$f" ]]; then
      return 0
    fi
  done
  return 1
}

is_allowed_root_dir() {
  local name="$1"

  # runner technical folder (always ignore)
  if [[ "$name" == ".git" ]]; then
    return 0
  fi

  # canonization root allows ONLY dot-folders (includes .github, .gate, .deploy, etc.)
  if [[ "$name" == .* ]]; then
    return 0
  fi

  return 1
}

# list root entries (names only)
while IFS= read -r entry; do
  [[ -n "$entry" ]] || continue

  # ignore current/parent
  if [[ "$entry" == "." || "$entry" == ".." ]]; then
    continue
  fi

  # ignore .git technically, but do not validate contents
  if [[ "$entry" == ".git" ]]; then
    continue
  fi

  full="$REPO_ROOT/$entry"

  if [[ -d "$full" ]]; then
    if ! is_allowed_root_dir "$entry"; then
      issues+=(" - Non-dot folder in root: $entry")
      fail=1
    fi
  else
    if ! is_allowed_root_file "$entry"; then
      issues+=(" - Unexpected root file: $entry")
      fail=1
    fi
  fi
done < <(cd "$REPO_ROOT" && ls -A)

# required root files must exist as regular files
for req in "${required_files[@]}"; do
  if [[ ! -f "$REPO_ROOT/$req" ]]; then
    issues+=(" - Missing required root file: $req")
    fail=1
  fi
done

if [[ "$fail" == "1" ]]; then
  echo ""
  echo "Root contract FAILED:"
  echo ""
  for i in "${issues[@]}"; do
    echo "$i"
  done

  mkdir -p "$REPO_ROOT/.report"
  : > "$REPO_ROOT/.report/gate-flag-root-contract.fail"

  exit 2
fi

echo "Root contract OK"
exit 0
