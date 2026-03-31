#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / '.antora-src'
PAGES_DIR = OUT_DIR / 'modules' / 'ROOT' / 'pages'
COMPONENT_DIR = PAGES_DIR / 'component'


def capture_component_pages() -> dict[str, bytes]:
    preserved: dict[str, bytes] = {}
    if not COMPONENT_DIR.exists():
        return preserved

    for path in COMPONENT_DIR.rglob('*'):
        if not path.is_file():
            continue
        rel = path.relative_to(COMPONENT_DIR).as_posix()
        if rel == 'index.adoc':
            continue
        preserved[rel] = path.read_bytes()

    return preserved


def restore_component_pages(preserved: dict[str, bytes]) -> None:
    for rel, payload in preserved.items():
        target = COMPONENT_DIR / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)


preserved_component_pages = capture_component_pages()

subprocess.run(['python3', str(ROOT / 'tools' / 'build_antora_site_v13.py')], check=True)

restore_component_pages(preserved_component_pages)
