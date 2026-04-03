#!/usr/bin/env python3
from __future__ import annotations

"""Copy generated Quality Atlas dashboard into the final public site build.

This script must run *after* Antora finishes writing `.site_build`.
It publishes the generated HTML dashboard into the final static site surface.
"""

from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'doc' / 'quality-atlas' / 'component_quality_dashboard.html'
TARGET_DIR = ROOT / '.site_build' / 'quality-atlas'
TARGET = TARGET_DIR / 'component_quality_dashboard.html'


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f'Missing Quality Atlas dashboard source: {SOURCE}')
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE, TARGET)


if __name__ == '__main__':
    main()
