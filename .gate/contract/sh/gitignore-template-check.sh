\
#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
POLICY_PATH="${GATE_GITIGNORE_POLICY:-$ROOT/.gate/policy/acceptable/gitignore-template.yml}"

if [[ ! -f "$POLICY_PATH" ]]; then
  echo ".gitignore template FAILED:"
  echo " - missing policy: $POLICY_PATH"
  exit 3
fi

# policy file is JSON (valid YAML), so we can parse via python json
REQ_LINES="$(python3 - "$POLICY_PATH" <<'PY'
import json, sys
p = sys.argv[1]
with open(p, "r", encoding="utf-8") as f:
  data = json.load(f)
req = data.get("template", {}).get("required", [])
for x in req:
  print(x)
PY
)"

GITIGNORE_PATH="$ROOT/.gitignore"
if [[ ! -f "$GITIGNORE_PATH" ]]; then
  echo ".gitignore template FAILED:"
  echo ""
  echo " - missing: .gitignore"
  exit 3
fi

missing=()
while IFS= read -r line; do
  [[ -n "$line" ]] || continue
  if ! grep -Fxq -- "$line" "$GITIGNORE_PATH"; then
    missing+=("$line")
  fi
done <<< "$REQ_LINES"

if [[ "${#missing[@]}" -gt 0 ]]; then
  echo ".gitignore template FAILED:"
  echo ""
  for m in "${missing[@]}"; do
    echo " - missing: $m"
    echo ""
  done
  exit 3
fi

echo ".gitignore template OK"
exit 0
