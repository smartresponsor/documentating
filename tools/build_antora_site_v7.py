#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / '.antora-src'
PAGES_DIR = OUT_DIR / 'modules' / 'ROOT' / 'pages'
NAV_FILE = OUT_DIR / 'modules' / 'ROOT' / 'nav.adoc'

subprocess.run(['python3', str(ROOT / 'tools' / 'build_antora_site_v6.py')], check=True)

(PAGES_DIR / 'support').mkdir(parents=True, exist_ok=True)

NAV_FILE.write_text(
    '* xref:index.adoc[Home]\n'
    '* xref:about/index.adoc[About]\n'
    '* xref:owner/index.adoc[Owner]\n'
    '* xref:article/index.adoc[Articles]\n'
    '* xref:component/index.adoc[Components]\n'
    '* xref:manifest/index.adoc[Manifests]\n'
    '* xref:support/index.adoc[Support]\n'
    '* xref:contact/index.adoc[Contact]\n'
    '* xref:privacy/index.adoc[Privacy]\n'
    '* xref:terms/index.adoc[Terms]\n',
    encoding='utf-8',
)

(PAGES_DIR / 'index.adoc').write_text('''= Oleksandr Tishchenko
:description: Owner-oriented public portal for Smartresponsor articles, components, manifests, strategic essays, and support.

This portal is the current owner-oriented public entry point for *Oleksandr Tishchenko*, *Marketing America Corp*, and *Smartresponsor*.

== What This Portal Covers

* xref:article/index.adoc[Articles] — public essays, technical positioning, and strategic notes.
* xref:component/index.adoc[Components] — public entry points for ecosystem components.
* xref:manifest/index.adoc[Manifests] — canon, statements, and owner-level notes.
* xref:about/index.adoc[About] — what this portal is and how it should be read.
* xref:owner/index.adoc[Owner] — who stands behind the portal.
* xref:contact/index.adoc[Contact] — contact scope and owner-controlled contact page.
* xref:support/index.adoc[Support] — owner-oriented support and sponsorship page.

== Positioning Themes

* AI is a stack, not just a chat interface.
* AI reveals the quality of thinking.
* Serious automation should prefer protocol and determinism over human imitation.
* Commerce is shifting toward agent-ready protocol logic.
* Execution needs accountability and evidence.

== Selected Reads

* xref:article/ai-is-not-just-chatgpt-five-layer-stack.adoc[AI Is Not Just ChatGPT]
* xref:article/ai-does-not-replace-thinking-it-reveals-its-quality.adoc[AI Does Not Replace Thinking. It Reveals Its Quality.]
* xref:article/do-not-scale-the-imitation-of-a-human.adoc[Do Not Scale the Imitation of a Human]
* xref:article/why-the-next-e-commerce-will-not-be-a-store-with-ai.adoc[Why the Next E-Commerce Will Not Be a Store with AI]
* xref:article/odyssey-execution-control-plane.adoc[Odyssey: The Execution Control Plane for AI]
* xref:article/the-first-great-war-between-platforms-and-protocols.adoc[The First Great War Between Platforms and Protocols]

== Support

If this portal and its materials are useful to you, see the dedicated xref:support/index.adoc[Support] page.

== Owner Anchors

* Oleksandr Tishchenko
* Marketing America Corp
* Smartresponsor
''', encoding='utf-8')

(PAGES_DIR / 'support' / 'index.adoc').write_text('''= Support Smartresponsor Documentation
:description: Owner-oriented support page for the Smartresponsor documentation portal.

This documentation portal is maintained directly by *Oleksandr Tishchenko*.

Support helps sustain:

* ongoing documentation maintenance,
* architecture and canon updates,
* implementation notes and examples,
* long-term continuity of the public documentation layer.

== Owner

* Oleksandr Tishchenko

== Company

* Marketing America Corp

== Organization

* High Hopes

== Contact

mailto:dev@smartresponsor.com[dev@smartresponsor.com]

== Sponsorship

If this documentation is useful to you, you can support it here:

https://github.com/sponsors/taa0662621456[Sponsor on GitHub]
''', encoding='utf-8')
