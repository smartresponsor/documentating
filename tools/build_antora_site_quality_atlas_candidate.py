#!/usr/bin/env python3
from __future__ import annotations

"""Shadow builder candidate for Quality Atlas integration.

This file intentionally does not replace `tools/build_antora_site.py`.
It runs the current canonical builder first and then layers in three
Quality Atlas surfaces into the generated Antora tree:

1. a canonical atlas page under `quality-atlas/`
2. a nav entry for `Quality Atlas`
3. a small home-page summary block framed as pre-RC / before v1

Use this file only as a candidate integration path in an isolated branch.
"""

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_BUILDER = ROOT / 'tools' / 'build_antora_site.py'
OUT_DIR = ROOT / '.antora-src'
PAGES_DIR = OUT_DIR / 'modules' / 'ROOT' / 'pages'
NAV_FILE = OUT_DIR / 'modules' / 'ROOT' / 'nav.adoc'
ATLAS_SUMMARY_SOURCE = ROOT / 'doc' / 'quality-atlas' / 'component-quality-summary.adoc'
ATLAS_HOME_BLOCK_SOURCE = ROOT / 'doc' / 'quality-atlas' / 'home-quality-atlas-block.adoc'
ATLAS_PAGE_TARGET = PAGES_DIR / 'quality-atlas' / 'component-quality-summary.adoc'
HOME_PAGE_TARGET = PAGES_DIR / 'index.adoc'
ATLAS_NAV_LINE = '* xref:quality-atlas/component-quality-summary.adoc[Quality Atlas]'
HOME_INSERT_BEFORE = '== Selected Reads'


def ensure(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def append_nav_entry() -> None:
    if not NAV_FILE.exists():
        return
    lines = NAV_FILE.read_text(encoding='utf-8').splitlines()
    if ATLAS_NAV_LINE in lines:
        return
    lines.append(ATLAS_NAV_LINE)
    NAV_FILE.write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')


def write_atlas_page() -> None:
    if not ATLAS_SUMMARY_SOURCE.exists():
        return
    ensure(ATLAS_PAGE_TARGET.parent)
    ATLAS_PAGE_TARGET.write_text(ATLAS_SUMMARY_SOURCE.read_text(encoding='utf-8').rstrip() + '\n', encoding='utf-8')


def inject_home_block() -> None:
    if not HOME_PAGE_TARGET.exists() or not ATLAS_HOME_BLOCK_SOURCE.exists():
        return
    home = HOME_PAGE_TARGET.read_text(encoding='utf-8')
    block = ATLAS_HOME_BLOCK_SOURCE.read_text(encoding='utf-8').rstrip() + '\n\n'
    if '== Quality Atlas' in home:
        return
    if HOME_INSERT_BEFORE in home:
        home = home.replace(HOME_INSERT_BEFORE, block + HOME_INSERT_BEFORE, 1)
    else:
        home = home.rstrip() + '\n\n' + block
    HOME_PAGE_TARGET.write_text(home.rstrip() + '\n', encoding='utf-8')


def main() -> None:
    subprocess.run(['python3', str(CANONICAL_BUILDER)], check=True)
    write_atlas_page()
    append_nav_entry()
    inject_home_block()


if __name__ == '__main__':
    main()
