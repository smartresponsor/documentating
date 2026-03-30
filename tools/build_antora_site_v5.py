#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / '.antora-src'
PAGES_DIR = OUT_DIR / 'modules' / 'ROOT' / 'pages'

subprocess.run(['python3', str(ROOT / 'tools' / 'build_antora_site_v4.py')], check=True)

article_index = PAGES_DIR / 'article' / 'index.adoc'
text = article_index.read_text(encoding='utf-8')
text = text.replace('[NOTE]\n====\nAsciiDoc is the canonical article source format. Legacy duplicates and noisy source artifacts are filtered out during publication.\n====\n\n', '')
text = re.sub(r' — (ADOC|MD)(?= —|$)', '', text)
text = re.sub(r' — (ADOC|MD)\n', '\n', text)
article_index.write_text(text, encoding='utf-8')

antora_yml = OUT_DIR / 'antora.yml'
antora_yml.write_text('name: ROOT\ntitle: Oleksandr Tishchenko\nversion: ~\nnav:\n  - modules/ROOT/nav.adoc\n', encoding='utf-8')

home = PAGES_DIR / 'index.adoc'
home.write_text('= Oleksandr Tishchenko\n:description: Owner-oriented public portal for articles, manifests, and component entry points.\n\nThis is the current owner-oriented documentation entry point.\n\n* xref:article/index.adoc[Articles]\n* xref:component/index.adoc[Components]\n* xref:manifest/index.adoc[Manifests]\n\n== Owner\n\n* Oleksandr Tishchenko\n* Marketing America Corp\n* Smart Responsor\n', encoding='utf-8')

(PAGES_DIR / 'contact').mkdir(parents=True, exist_ok=True)
(PAGES_DIR / 'privacy').mkdir(parents=True, exist_ok=True)
(PAGES_DIR / 'terms').mkdir(parents=True, exist_ok=True)

(PAGES_DIR / 'contact' / 'index.adoc').write_text('= Contact\n:description: Contact and inquiry page for Oleksandr Tishchenko, Marketing America Corp, and Smart Responsor.\n\nThis documentation site is currently owner-oriented and maintained by *Oleksandr Tishchenko*.\n\n== Contact Scope\n\nFor collaboration, publication, and owner-level inquiries related to this documentation portal, Smart Responsor, or Marketing America Corp, use the official channels you already have for this project.\n\n== Contact Details\n\nA dedicated owner-controlled contact block can be placed here.\n', encoding='utf-8')
(PAGES_DIR / 'privacy' / 'index.adoc').write_text('= Privacy Policy\n:description: Privacy policy placeholder for the owner-oriented documentation portal.\n\nThis section is reserved for the privacy policy of the public documentation portal.\n', encoding='utf-8')
(PAGES_DIR / 'terms' / 'index.adoc').write_text('= Terms\n:description: Terms placeholder for the owner-oriented documentation portal.\n\nThis section is reserved for the terms and related public legal notices of the documentation portal.\n', encoding='utf-8')
