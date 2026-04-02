#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / 'doc' / 'quality-baseline'
OUT_DIR = ROOT / '.antora-src' / 'modules' / 'ROOT' / 'pages' / 'quality-atlas'
NAV_FILE = ROOT / '.antora-src' / 'modules' / 'ROOT' / 'nav.adoc'
HOME_FILE = ROOT / '.antora-src' / 'modules' / 'ROOT' / 'pages' / 'index.adoc'

PAGE_ORDER = [
    ('overview.adoc', 'Overview'),
    ('quality-baseline.adoc', 'Quality Baseline'),
    ('principles.adoc', 'Principles'),
    ('architectural-dimensions.adoc', 'Architectural Dimensions'),
    ('readiness-model.adoc', 'Readiness Model'),
    ('evaluation.adoc', 'Evaluation'),
    ('glossary.adoc', 'Glossary'),
]


def ensure(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write(path: Path, content: str) -> None:
    ensure(path.parent)
    path.write_text(content.rstrip() + '\n', encoding='utf-8')


def copy_pages() -> None:
    ensure(OUT_DIR)
    for filename, _ in PAGE_ORDER:
        source = SOURCE_DIR / filename
        if source.exists():
            write(OUT_DIR / filename, source.read_text(encoding='utf-8'))


def build_index() -> None:
    links = '\n'.join(f'* xref:quality-atlas/{filename}[{title}]' for filename, title in PAGE_ORDER)
    write(
        OUT_DIR / 'index.adoc',
        f'''= Quality Atlas
:description: Engineering quality baseline, readiness model, evaluation layer, and pre-RC comparative atlas for the Smartresponsor ecosystem.

This section is the umbrella quality surface for the Smartresponsor ecosystem.

It combines:

* a normative engineering baseline,
* a readiness and evaluation layer,
* and a comparative pre-RC atlas surface.

== Start Here

{links}
* xref:quality-atlas/explorer.adoc[Explorer]

== Pre-RC Atlas Snapshot

include::summary.adoc[]
''',
    )


def patch_nav() -> None:
    if not NAV_FILE.exists():
        return
    nav = NAV_FILE.read_text(encoding='utf-8')
    block = '''* xref:quality-atlas/index.adoc[Quality Atlas]
** xref:quality-atlas/overview.adoc[Overview]
** xref:quality-atlas/quality-baseline.adoc[Quality Baseline]
** xref:quality-atlas/principles.adoc[Principles]
** xref:quality-atlas/architectural-dimensions.adoc[Architectural Dimensions]
** xref:quality-atlas/readiness-model.adoc[Readiness Model]
** xref:quality-atlas/evaluation.adoc[Evaluation]
** xref:quality-atlas/glossary.adoc[Glossary]
** xref:quality-atlas/explorer.adoc[Explorer]
'''
    if 'xref:quality-atlas/index.adoc[Quality Atlas]' in nav:
        return
    marker = '* xref:manifest/index.adoc[Manifests]\n'
    if marker in nav:
        nav = nav.replace(marker, block + marker)
    else:
        nav += '\n' + block
    write(NAV_FILE, nav)


def patch_home() -> None:
    if not HOME_FILE.exists():
        return
    text = HOME_FILE.read_text(encoding='utf-8')
    bullet = '* xref:quality-atlas/index.adoc[Quality Atlas] — engineering baseline, readiness model, evaluation layer, and comparative pre-RC atlas.\n'
    target = '* xref:component/index.adoc[Components] — entry points for ecosystem components and directions.\n'
    if bullet not in text and target in text:
        text = text.replace(target, target + bullet)
    write(HOME_FILE, text)


def main() -> None:
    copy_pages()
    build_index()
    patch_nav()
    patch_home()


if __name__ == '__main__':
    main()
