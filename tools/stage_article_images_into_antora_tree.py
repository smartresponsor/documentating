#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / 'docs' / 'article' / 'images'
TARGET_DIR = ROOT / '.antora-src' / 'modules' / 'ROOT' / 'pages' / 'article' / 'images'


def main() -> None:
    if not SOURCE_DIR.exists():
        print(f'No article image source directory found: {SOURCE_DIR}')
        return

    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    copied = 0
    for path in sorted(SOURCE_DIR.iterdir()):
        if not path.is_file():
            continue
        shutil.copy2(path, TARGET_DIR / path.name)
        copied += 1

    print(f'Staged {copied} article images into {TARGET_DIR}')


if __name__ == '__main__':
    main()
