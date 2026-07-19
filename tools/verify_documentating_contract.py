#!/usr/bin/env python3
from __future__ import annotations

"""Verify the release-critical Documentating repository contract."""

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    'README.md',
    'package.json',
    'package-lock.json',
    'requirements.txt',
    'antora-playbook.yml',
    'tools/build_antora_site.py',
    'tools/run_antora.mjs',
    'tools/run_python.mjs',
    '.github/workflows/gh-pages.yml',
    '.sync/manifest/component-list.yml',
    'docs/component/documentating/index.md',
    'supplemental-ui/img/marketing-america-corp-mark.svg',
)
FORBIDDEN_COMPONENT_MARKERS = ('TODO', 'FIXME', 'PLACEHOLDER', '**stub**')
FORBIDDEN_RUNTIME_PATHS = ('src/Controller', 'config/routes.yaml', 'config/routes')


def fail(message: str) -> None:
    print(f'[documentating-contract] ERROR: {message}', file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        fail(f"missing required files: {', '.join(missing)}")

    package = json.loads((ROOT / 'package.json').read_text(encoding='utf-8'))
    scripts = package.get('scripts') or {}
    for script in ('verify:content', 'test', 'build:content', 'build'):
        if not scripts.get(script):
            fail(f'missing npm script: {script}')

    requirements = (ROOT / 'requirements.txt').read_text(encoding='utf-8').splitlines()
    if 'PyYAML==6.0.2' not in requirements:
        fail('requirements.txt must pin PyYAML==6.0.2')

    playbook = (ROOT / 'antora-playbook.yml').read_text(encoding='utf-8')
    if 'start_page: ROOT::index.adoc' not in playbook:
        fail('Antora start_page must remain ROOT::index.adoc')
    if 'dir: .site_build' not in playbook:
        fail('Antora output directory must remain .site_build')

    manifest = (ROOT / '.sync/manifest/component-list.yml').read_text(encoding='utf-8')
    if not any(line.strip() == '- Documentating' for line in manifest.splitlines()):
        fail('component registry does not contain Documentating')

    header = (ROOT / 'supplemental-ui/partials/header-content.hbs').read_text(encoding='utf-8')
    footer = (ROOT / 'supplemental-ui/partials/footer.hbs').read_text(encoding='utf-8')
    for required_brand_token in (
        'marketing-america-corp-mark.svg',
        'Marketing America Corp',
        'High Hopes',
    ):
        if required_brand_token not in header and required_brand_token not in footer:
            fail(f'missing required branding token: {required_brand_token}')

    component_page = (ROOT / 'docs/component/documentating/index.md').read_text(encoding='utf-8')
    for marker in FORBIDDEN_COMPONENT_MARKERS:
        if marker.lower() in component_page.lower():
            fail(f'Documentating component page contains forbidden marker: {marker}')

    for relative_path in FORBIDDEN_RUNTIME_PATHS:
        if (ROOT / relative_path).exists():
            fail(f'foreign runtime ownership detected: {relative_path}')

    print('[documentating-contract] OK')


if __name__ == '__main__':
    main()
