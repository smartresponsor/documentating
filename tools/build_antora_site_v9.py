#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / '.antora-src'
PAGES_DIR = OUT_DIR / 'modules' / 'ROOT' / 'pages'

subprocess.run(['python3', str(ROOT / 'tools' / 'build_antora_site_v7.py')], check=True)

(PAGES_DIR / 'contact').mkdir(parents=True, exist_ok=True)
(PAGES_DIR / 'contact' / 'index.adoc').write_text('''= Contact
:description: Contact page for Marketing America Corp, High Hopes, Oleksandr Tishchenko, and Smartresponsor.

This portal is currently maintained in an owner-oriented mode.

== Contact

* Marketing America Corp
* High Hopes
* Oleksandr Tishchenko
* mailto:dev@smartresponsor.com[dev@smartresponsor.com]
''', encoding='utf-8')
