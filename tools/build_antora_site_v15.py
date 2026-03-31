#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / '.antora-src'
PAGES_DIR = OUT_DIR / 'modules' / 'ROOT' / 'pages'
COMPONENT_DIR = PAGES_DIR / 'component'
MANIFEST_FILE = ROOT / '.sync' / 'manifest' / 'component-list.yml'


def load_slug_overrides() -> dict[str, str]:
    if not MANIFEST_FILE.exists():
        return {}
    payload = yaml.safe_load(MANIFEST_FILE.read_text(encoding='utf-8')) or {}
    raw = payload.get('slug_overrides') or {}
    return {str(k): str(v) for k, v in raw.items()}


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


def expand_with_slug_overrides(preserved: dict[str, bytes], overrides: dict[str, str]) -> dict[str, bytes]:
    expanded = dict(preserved)
    for source_slug, target_slug in overrides.items():
        source_prefix = f'{source_slug}/'
        target_prefix = f'{target_slug}/'
        for rel, payload in list(preserved.items()):
            if rel.startswith(source_prefix):
                target_rel = target_prefix + rel[len(source_prefix):]
                expanded[target_rel] = payload
    return expanded


def restore_component_pages(preserved: dict[str, bytes]) -> None:
    for rel, payload in preserved.items():
        target = COMPONENT_DIR / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)


slug_overrides = load_slug_overrides()
preserved_component_pages = capture_component_pages()
preserved_component_pages = expand_with_slug_overrides(preserved_component_pages, slug_overrides)

subprocess.run(['python3', str(ROOT / 'tools' / 'build_antora_site_v13.py')], check=True)

restore_component_pages(preserved_component_pages)
