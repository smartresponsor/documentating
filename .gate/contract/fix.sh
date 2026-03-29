#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-.}"
PROPOSAL_PATH="${2:-.report/gate-fix-proposal.ndjson}"
MODE="${3:-print}" # print | safe | dangerous

cd "$REPO_ROOT"

if [[ ! -f "$PROPOSAL_PATH" ]]; then
  echo "[gate] no proposal file: $PROPOSAL_PATH"
  exit 0
fi

python3 - <<'PY'
import os, json, hashlib, re, shutil, subprocess, sys

proposal_path = os.environ.get("PROPOSAL_PATH", ".report/gate-fix-proposal.ndjson")
mode = os.environ.get("MODE", "print")

def sha256(path: str) -> str:
    if not os.path.exists(path): return ""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def is_safe(p: dict) -> bool:
    op = p.get("op","")
    if op in {"file.append_lines","file.ensure_exists","path.ensure_dir","chmod.add_x","report.print"}:
        return True
    if op == "file.write_text" and p.get("guard","") == "missing_only":
        return True
    return False

def apply_append_lines(p):
    path = p["path"]
    ensure_dir(os.path.dirname(path) or ".")
    if not os.path.exists(path):
        open(path, "w", encoding="utf-8").close()
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        cur = f.read().splitlines()
    need = [x for x in p.get("lines", []) if x not in cur]
    if need:
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n# gate: append_lines\n")
            f.write("\n".join(need))
            f.write("\n")
        print(f"[gate] applied file.append_lines path={path} added={len(need)}")
    else:
        print(f"[gate] noop file.append_lines path={path}")

def apply_ensure_exists(p):
    path = p["path"]
    ensure_dir(os.path.dirname(path) or ".")
    if not os.path.exists(path):
        open(path, "w", encoding="utf-8").close()
        print(f"[gate] applied file.ensure_exists path={path}")
    else:
        print(f"[gate] noop file.ensure_exists path={path}")

def apply_write_text(p):
    path = p["path"]
    ensure_dir(os.path.dirname(path) or ".")
    guard = p.get("guard","")
    if guard == "missing_only":
        if os.path.exists(path):
            print(f"[gate] skip file.write_text (exists, missing_only) path={path}")
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(p.get("text",""))
        print(f"[gate] applied file.write_text (missing_only) path={path}")
        return
    if guard == "sha256":
        expected = (p.get("expected","") or "").lower()
        actual = sha256(path)
        if actual != expected:
            print(f"[gate] skip file.write_text (sha256 mismatch) path={path}")
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(p.get("text",""))
        print(f"[gate] applied file.write_text (sha256 ok) path={path}")
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(p.get("text",""))
    print(f"[gate] applied file.write_text (unguarded) path={path}")

def apply_ensure_dir(p):
    path = p["path"]
    ensure_dir(path)
    print(f"[gate] applied path.ensure_dir path={path}")

def apply_chmod_add_x(p):
    path = p["path"]
    if not os.path.exists(path):
        print(f"[gate] skip chmod.add_x (missing) path={path}")
        return
    try:
        subprocess.run(["chmod","+x",path], check=True)
        print(f"[gate] applied chmod.add_x path={path}")
    except Exception as e:
        print(f"[gate] skip chmod.add_x path={path} err={e}")

def apply_report_print(p):
    print(f"[gate] proposal: {p.get('text','')}")

def apply_agent_required(p):
    scope = p.get("scope",[])
    prompt = p.get("prompt","")
    print(f"[gate] agent.required scope={','.join(scope)} prompt={prompt}")

handlers = {
    "file.append_lines": apply_append_lines,
    "file.ensure_exists": apply_ensure_exists,
    "file.write_text": apply_write_text,
    "path.ensure_dir": apply_ensure_dir,
    "chmod.add_x": apply_chmod_add_x,
    "report.print": apply_report_print,
    "agent.required": apply_agent_required,
}

with open(proposal_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = [ln.strip() for ln in f.readlines() if ln.strip()]

print(f"[gate] proposal file: {proposal_path} entries={len(lines)}")

for ln in lines:
    try:
        p = json.loads(ln)
    except Exception:
        print("[gate] skip bad json line")
        continue

    op = p.get("op","")
    if not op:
        print("[gate] skip proposal without op")
        continue

    lvl = p.get("level","")
    note = p.get("note","")
    print(f"[gate] proposal op={op} level={lvl} note={note}")

    if mode == "print":
        continue
    if mode == "safe" and not is_safe(p):
        continue

    fn = handlers.get(op)
    if not fn:
        print(f"[gate] unsupported op={op} (skip)")
        continue

    fn(p)
PY
