#!/usr/bin/env python3
from __future__ import annotations

"""Shadow builder candidate for live-repo asset copy fix.

This file intentionally does not replace `tools/build_antora_site.py`.
It runs the current canonical builder first and then overlays root-level
`assets/` into the generated Antora asset surface.

Use this file only as a candidate replacement path while evaluating the
live-repo action fix in an isolated branch.
"""

from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_BUILDER = ROOT / 'tools' / 'build_antora_site.py'
SOURCE_DIR = ROOT / 'assets'
TARGET_DIR = ROOT / '.antora-src' / 'modules' / 'ROOT' / 'assets' / 'images'


def ensure(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def overlay_root_assets() -> None:
    if not SOURCE_DIR.exists():
        return
    ensure(TARGET_DIR)
    for path in sorted(SOURCE_DIR.iterdir()):
        if path.is_file():
            shutil.copy2(path, TARGET_DIR / path.name)


def main() -> None:
    subprocess.run(['python3', str(CANONICAL_BUILDER)], check=True)
    overlay_root_assets()


if __name__ == '__main__':
    main()
