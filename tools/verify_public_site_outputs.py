#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = ROOT / '.site_build'

REQUIRED_ROOT_FILES = {
    'robots.txt': 'Sitemap: https://docs.smartresponsor.com/sitemap.xml',
    'llms.txt': 'https://docs.smartresponsor.com',
    'sitemap.xml': '<urlset',
}

REQUIRED_HEAD_SNIPPETS = [
    'rel="canonical"',
    'property="og:title"',
    'property="og:description"',
    'name="twitter:card"',
    'application/ld+json',
]


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def check_root_files(errors: list[str]) -> None:
    for relative, expected in REQUIRED_ROOT_FILES.items():
        path = SITE_DIR / relative
        require(path.exists(), f'missing root publication file: {relative}', errors)
        if path.exists():
            content = read_text(path)
            require(expected in content, f'root publication file missing expected content: {relative} -> {expected}', errors)


def check_head(path: Path, errors: list[str]) -> None:
    content = read_text(path)
    for snippet in REQUIRED_HEAD_SNIPPETS:
        require(snippet in content, f'missing head metadata in {path.relative_to(SITE_DIR).as_posix()}: {snippet}', errors)


def main() -> int:
    errors: list[str] = []
    require(SITE_DIR.exists(), '.site_build was not generated', errors)
    if errors:
        for error in errors:
            print(f'ERROR: {error}')
        return 1

    check_root_files(errors)

    index_path = SITE_DIR / 'index.html'
    require(index_path.exists(), 'missing generated home page: index.html', errors)
    if index_path.exists():
        check_head(index_path, errors)

    article_index = SITE_DIR / 'article' / 'index.html'
    require(article_index.exists(), 'missing generated article index page', errors)
    if article_index.exists():
        check_head(article_index, errors)

    if errors:
        for error in errors:
            print(f'ERROR: {error}')
        return 1

    print('OK: public surface outputs verified (robots, llms, sitemap, canonical, OG/Twitter, JSON-LD).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
