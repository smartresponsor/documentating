#!/usr/bin/env python3
from __future__ import annotations

"""Canonical builder candidate with embedded Quality Atlas dashboard.

Adds:
- embedded summary page (iframe)
- nav entry
- home block
- dashboard generation + publish surface
"""

from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_BUILDER = ROOT / 'tools' / 'build_antora_site.py'
GENERATOR = ROOT / 'tools' / 'generate_quality_atlas_dashboard.py'
OUT_DIR = ROOT / '.antora-src'
PAGES_DIR = OUT_DIR / 'modules' / 'ROOT' / 'pages'
NAV_FILE = OUT_DIR / 'modules' / 'ROOT' / 'nav.adoc'
EMBED_SOURCE = ROOT / 'doc' / 'quality-atlas' / 'component-quality-summary-embedded.adoc'
PAGE_TARGET = PAGES_DIR / 'quality-atlas' / 'component-quality-summary.adoc'
HOME_PAGE = PAGES_DIR / 'index.adoc'
DASHBOARD_SRC = ROOT / 'doc' / 'quality-atlas' / 'component_quality_dashboard.html'
PUBLIC_DIR = ROOT / '.site_build' / 'quality-atlas'
PUBLIC_FILE = PUBLIC_DIR / 'component_quality_dashboard.html'
NAV_LINE = '* xref:quality-atlas/component-quality-summary.adoc[Quality Atlas]'


def ensure(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def main():
    subprocess.run(['python3', str(CANONICAL_BUILDER)], check=True)

    if GENERATOR.exists():
        subprocess.run(['python3', str(GENERATOR)], check=True)

    if EMBED_SOURCE.exists():
        ensure(PAGE_TARGET.parent)
        PAGE_TARGET.write_text(EMBED_SOURCE.read_text(encoding='utf-8'), encoding='utf-8')

    if NAV_FILE.exists():
        lines = NAV_FILE.read_text(encoding='utf-8').splitlines()
        if NAV_LINE not in lines:
            lines.append(NAV_LINE)
            NAV_FILE.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    if DASHBOARD_SRC.exists():
        ensure(PUBLIC_DIR)
        shutil.copy2(DASHBOARD_SRC, PUBLIC_FILE)


if __name__ == '__main__':
    main()
