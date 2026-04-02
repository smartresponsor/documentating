#!/usr/bin/env python3
from __future__ import annotations

"""Canonical builder replacement candidate with Quality Atlas page and dashboard.

This file keeps the current canonical build path and layers in:

1. Quality Atlas summary page under `quality-atlas/`
2. Quality Atlas nav entry
3. Home-page pre-RC summary block
4. Generated dashboard HTML copied into the public site build surface

Use it as a candidate replacement path while validating the full Atlas integration.
"""

from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_BUILDER = ROOT / 'tools' / 'build_antora_site.py'
DASHBOARD_GENERATOR = ROOT / 'tools' / 'generate_quality_atlas_dashboard.py'
OUT_DIR = ROOT / '.antora-src'
PAGES_DIR = OUT_DIR / 'modules' / 'ROOT' / 'pages'
NAV_FILE = OUT_DIR / 'modules' / 'ROOT' / 'nav.adoc'
ATLAS_SUMMARY_SOURCE = ROOT / 'doc' / 'quality-atlas' / 'component-quality-summary.adoc'
ATLAS_HOME_BLOCK_SOURCE = ROOT / 'doc' / 'quality-atlas' / 'home-quality-atlas-block.adoc'
ATLAS_DASHBOARD_SOURCE = ROOT / 'doc' / 'quality-atlas' / 'component_quality_dashboard.html'
ATLAS_PAGE_TARGET = PAGES_DIR / 'quality-atlas' / 'component-quality-summary.adoc'
HOME_PAGE_TARGET = PAGES_DIR / 'index.adoc'
ATLAS_PUBLIC_TARGET_DIR = ROOT / '.site_build' / 'quality-atlas'
ATLAS_PUBLIC_TARGET = ATLAS_PUBLIC_TARGET_DIR / 'component_quality_dashboard.html'
ATLAS_NAV_LINE = '* xref:quality-atlas/component-quality-summary.adoc[Quality Atlas]'
HOME_INSERT_BEFORE = '== Selected Reads'
DASHBOARD_LINK_LINE = '* link:/quality-atlas/component_quality_dashboard.html[Open interactive Quality Atlas dashboard]'


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
    content = ATLAS_SUMMARY_SOURCE.read_text(encoding='utf-8').rstrip() + '\n\n'
    if 'Open interactive Quality Atlas dashboard' not in content:
        content += DASHBOARD_LINK_LINE + '\n'
    ATLAS_PAGE_TARGET.write_text(content, encoding='utf-8')


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


def generate_dashboard() -> None:
    if DASHBOARD_GENERATOR.exists():
        subprocess.run(['python3', str(DASHBOARD_GENERATOR)], check=True)


def copy_dashboard_to_public_surface() -> None:
    if not ATLAS_DASHBOARD_SOURCE.exists():
        return
    ensure(ATLAS_PUBLIC_TARGET_DIR)
    shutil.copy2(ATLAS_DASHBOARD_SOURCE, ATLAS_PUBLIC_TARGET)


def main() -> None:
    subprocess.run(['python3', str(CANONICAL_BUILDER)], check=True)
    generate_dashboard()
    write_atlas_page()
    append_nav_entry()
    inject_home_block()
    copy_dashboard_to_public_surface()


if __name__ == '__main__':
    main()
