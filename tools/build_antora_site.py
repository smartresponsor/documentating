#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / 'docs'
OUT_DIR = ROOT / '.antora-src'
PAGES_DIR = OUT_DIR / 'modules' / 'ROOT' / 'pages'
PARTIALS_DIR = OUT_DIR / 'modules' / 'ROOT' / 'partials'
COMPONENT_DIR = PAGES_DIR / 'component'
NAV_FILE = OUT_DIR / 'modules' / 'ROOT' / 'nav.adoc'
MANIFEST_FILE = ROOT / '.sync' / 'manifest' / 'component-list.yml'
DATE_PREFIX_RE = re.compile(r'^\d{4}-\d{2}-\d{2}--?')
ATTR_RE = re.compile(r'^:([^:]+):\s*(.*)$')
ASSET_IMAGE_RE = re.compile(r'image::/assets/([^\[]+)\[')
ADOC_INCLUDE_RE = re.compile(r'include::([^\[]+\.adoc)\[\]')
ARTICLE_DIRS = [DOCS_DIR / 'article']
SKIP_RELS = {
    'docs/article/2026-03-29-ai-is-not-just-chatgpt-five-layer-stack.adoc',
    'docs/article/2026-03-29-ai-ne-zamenyaet-myshlenie-obnazhaet-kachestvo.adoc',
    'docs/article/odyssey-who-is-announcement.adoc',
}
SKIP_SLUGS = {'tesr', 'test'}
PUBLIC_SECTIONS = [
    ('manifest', 'Manifests', 'Public manifest-style documents, boundary statements, and owner-level positions.'),
    ('principle', 'Principles', 'Reusable public principles and decision-interface patterns.'),
    ('glossary', 'Glossary', 'Shared terms used by the New Paradigm and Smartresponsor documentation.'),
]
QUALITY_GENERATORS = [
    'generate_quality_baseline_section.py',
    'generate_pre_rc_quality_atlas.py',
    'seed_quality_atlas_snapshots.py',
    'generate_quality_atlas_portfolio.py',
    'generate_quality_atlas_internal.py',
    'generate_quality_atlas_schedule.py',
]


@dataclass
class Page:
    title: str
    slug: str
    date: str
    description: str
    author: str
    tags: list[str]
    source_rel: str
    body_adoc: str
    source_rank: int
    include_only: bool = False


def ensure(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write(path: Path, content: str) -> None:
    ensure(path.parent)
    path.write_text(content.rstrip() + '\n', encoding='utf-8')


def slugify(value: str) -> str:
    value = DATE_PREFIX_RE.sub('', value.strip().lower()).replace('&', ' and ')
    value = re.sub(r'[\s_]+', '-', value)
    value = re.sub(r'[^a-z0-9\-]+', '-', value)
    return re.sub(r'-{2,}', '-', value).strip('-') or 'page'


def norm(value: str) -> str:
    return re.sub(r'[^a-z0-9]+', '', slugify(value))


def tags_of(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [part.strip() for part in str(value).split(',') if part.strip()]


def md_to_adoc(text: str) -> str:
    try:
        return subprocess.run(
            ['pandoc', '--from=gfm', '--to=asciidoc', '--wrap=none'],
            input=text,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
    except FileNotFoundError:
        converted: list[str] = []
        in_fence = False
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith('```'):
                converted.append('----')
                in_fence = not in_fence
                continue
            if in_fence:
                converted.append(line)
                continue
            heading = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading:
                converted.append(f"{'=' * (len(heading.group(1)) + 1)} {heading.group(2).strip()}")
                continue
            converted.append(re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'\2[\1]', line))
        return '\n'.join(converted).strip()


def normalize_adoc(text: str) -> str:
    text = ASSET_IMAGE_RE.sub(r'image::\1[', text)
    return ADOC_INCLUDE_RE.sub(r'include::partial$article/\1[]', text)


def derive_slug(explicit: str, title: str, path: Path) -> str:
    if explicit.strip():
        return explicit.strip()
    title_slug = slugify(title)
    path_slug = slugify(path.stem)
    if title_slug in {'page', 'chatgpt', 'article', 'post'} and path_slug not in {'page', title_slug}:
        return path_slug
    if any(ord(ch) > 127 for ch in title) and path_slug != 'page' and len(path_slug) >= 8:
        return path_slug
    return path_slug if title_slug == 'page' and path_slug != 'page' else title_slug


def parse_adoc(raw: str, path: Path, include_only: bool = False) -> Page:
    lines = raw.splitlines()
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    title = ''
    if i < len(lines) and lines[i].startswith('= '):
        title = lines[i][2:].strip()
        i += 1
    attrs: dict[str, str] = {}
    while i < len(lines):
        match = ATTR_RE.match(lines[i])
        if not match:
            break
        attrs[match.group(1).strip().lower()] = match.group(2).strip()
        i += 1
        if i < len(lines) and not lines[i].strip():
            i += 1
            break
    body = normalize_adoc('\n'.join(lines[i:]).lstrip())
    title = title or attrs.get('title', '') or path.stem
    slug = derive_slug(attrs.get('page-slug', '') or attrs.get('slug', ''), title, path)
    date = attrs.get('page-published') or attrs.get('date') or ''
    author = attrs.get('page-author') or attrs.get('author') or ''
    desc = attrs.get('description', '')
    tags = tags_of(attrs.get('page-tags') or attrs.get('tags'))
    source_rel = path.relative_to(ROOT).as_posix()
    if include_only:
        return Page(title, slug, date, desc, author, tags, source_rel, body + '\n', 2, True)
    head = [f'= {title}', f':page-slug: {slug}']
    if date:
        head.append(f':page-published: {date}')
    if author:
        head.append(f':page-author: {author}')
    if desc:
        head.append(f':description: {desc}')
    if tags:
        head.append(f":page-tags: {', '.join(tags)}")
    head.extend(['', f"_Source asciidoc: `{source_rel}`_", ''])
    return Page(title, slug, date, desc, author, tags, source_rel, '\n'.join(head) + body + '\n', 2)


def parse_md(raw: str, path: Path) -> Page:
    meta, body = ({}, raw)
    if raw.startswith('---\n') and '\n---\n' in raw:
        left, body = raw.split('\n---\n', 1)
        meta = yaml.safe_load(left[4:]) or {}
    title = str(meta.get('title', '')).strip()
    if not title:
        for line in body.splitlines():
            if line.strip().startswith('# '):
                title = line.strip()[2:].strip()
                break
    title = title or path.stem
    lines = body.splitlines()
    j = 0
    while j < len(lines) and not lines[j].strip():
        j += 1
    if j < len(lines) and lines[j].strip().startswith('# ') and lines[j].strip()[2:].strip() == title:
        body = '\n'.join(lines[j + 1:]).lstrip()
    source_rel = path.relative_to(ROOT).as_posix()
    slug = derive_slug(str(meta.get('slug', '')).strip(), title, path)
    date = str(meta.get('date', '')).strip().strip('"')
    author = str(meta.get('author', '')).strip()
    desc = str(meta.get('description', '')).strip()
    tags = tags_of(meta.get('tags'))
    head = [f'= {title}', f':page-slug: {slug}']
    if date:
        head.append(f':page-published: {date}')
    if author:
        head.append(f':page-author: {author}')
    if desc:
        head.append(f':description: {desc}')
    if tags:
        head.append(f":page-tags: {', '.join(tags)}")
    head.extend(['', f"_Source markdown: `{source_rel}`_", ''])
    return Page(title, slug, date, desc, author, tags, source_rel, '\n'.join(head) + md_to_adoc(body) + '\n', 1)


def skip(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    return rel in SKIP_RELS or path.name.lower().startswith('_') or path.name.lower() in {'index.md', 'index.adoc', 'article-template.adoc'}


def choose(current: Page | None, candidate: Page) -> Page:
    if current is None:
        return candidate
    return candidate if (candidate.source_rank, candidate.date, candidate.source_rel) > (current.source_rank, current.date, current.source_rel) else current


def collect(dirs: list[Path], allow_partials: bool = False) -> list[Page]:
    found: dict[str, Page] = {}
    adoc_titles: set[str] = set()
    adoc_slugs: set[str] = set()
    for directory in dirs:
        if not directory.exists():
            continue
        for path in sorted(directory.iterdir()):
            if not path.is_file() or skip(path) or path.suffix.lower() != '.adoc':
                continue
            page = parse_adoc(path.read_text(encoding='utf-8'), path, allow_partials and bool(re.search(r'-\d{2}$', path.stem)))
            if page.slug in SKIP_SLUGS or norm(page.title) == 'tesr':
                continue
            found[page.slug] = choose(found.get(page.slug), page)
            adoc_titles.add(norm(page.title))
            adoc_slugs.add(norm(page.slug))
    for directory in dirs:
        if not directory.exists():
            continue
        for path in sorted(directory.iterdir()):
            if not path.is_file() or skip(path) or path.suffix.lower() != '.md':
                continue
            page = parse_md(path.read_text(encoding='utf-8'), path)
            if page.slug in SKIP_SLUGS or norm(page.title) == 'tesr':
                continue
            if norm(page.title) in adoc_titles or norm(page.slug) in adoc_slugs:
                continue
            found[page.slug] = choose(found.get(page.slug), page)
    return sorted(found.values(), key=lambda page: (page.date, page.title.lower()), reverse=True)


def load_manifest_payload() -> dict:
    if not MANIFEST_FILE.exists():
        return {}
    return yaml.safe_load(MANIFEST_FILE.read_text(encoding='utf-8')) or {}


def load_components() -> list[tuple[str, str]]:
    payload = load_manifest_payload()
    overrides = payload.get('slug_overrides') or {}
    return [(str(name), str(overrides.get(str(name).lower(), str(name).lower()))) for name in payload.get('components') or []]


def load_slug_overrides() -> dict[str, str]:
    return {str(k): str(v) for k, v in (load_manifest_payload().get('slug_overrides') or {}).items()}


def capture_component_pages() -> dict[str, bytes]:
    if not COMPONENT_DIR.exists():
        return {}
    preserved: dict[str, bytes] = {}
    for path in COMPONENT_DIR.rglob('*'):
        if path.is_file():
            rel = path.relative_to(COMPONENT_DIR).as_posix()
            if rel != 'index.adoc':
                preserved[rel] = path.read_bytes()
    return preserved


def expand_overrides(preserved: dict[str, bytes], overrides: dict[str, str]) -> dict[str, bytes]:
    expanded = dict(preserved)
    for source_slug, target_slug in overrides.items():
        for rel, payload in list(preserved.items()):
            prefix = f'{source_slug}/'
            if rel.startswith(prefix):
                expanded[f'{target_slug}/' + rel[len(prefix):]] = payload
    return expanded


def restore_component_pages(preserved: dict[str, bytes]) -> None:
    for rel, payload in preserved.items():
        target = COMPONENT_DIR / rel
        ensure(target.parent)
        target.write_bytes(payload)


def suffix(page: Page) -> str:
    meta = [page.date] if page.date else []
    if page.description:
        meta.append(page.description)
    return f" — {' — '.join(meta)}" if meta else ''


def generate_index(section: str, title: str, description: str, pages: list[Page]) -> None:
    lines = [f'= {title}', f':description: {description}', '', description, '', '== Index', '']
    for page in pages:
        if page.include_only:
            write(PARTIALS_DIR / 'article' / f'{page.slug}.adoc', page.body_adoc)
            continue
        write(PAGES_DIR / section / f'{page.slug}.adoc', page.body_adoc)
        lines.append(f'* xref:{section}/{page.slug}.adoc[{page.title}]{suffix(page)}')
    if len(lines) == 7:
        lines.append('No public documents found yet.')
    write(PAGES_DIR / section / 'index.adoc', '\n'.join(lines))


def generate_components(components: list[tuple[str, str]]) -> None:
    lines = ['= Components', ':description: Public entry points for Smart Responsor ecosystem components.', '', 'This section is the public component map of the Smart Responsor ecosystem.', '', '== Index', '']
    for name, slug in components:
        lines.append(f'* xref:component/{slug}/index.adoc[{name}]')
        write(PAGES_DIR / 'component' / slug / 'index.adoc', f'= {name}\n\nThis is the public entry page for the *{name}* component.\n\nDetailed component documentation may later be sourced from the component repository and aggregated into the portal.\n\n* Canonical slug: `{slug}`\n')
    if len(lines) == 7:
        lines.append('No component registry found yet.')
    write(PAGES_DIR / 'component' / 'index.adoc', '\n'.join(lines))


def write_nav() -> None:
    lines = ['* xref:index.adoc[Home]', '* xref:article/index.adoc[Articles]']
    lines.extend(f'* xref:{slug}/index.adoc[{title}]' for slug, title, _ in PUBLIC_SECTIONS)
    lines.extend([
        '* xref:component/index.adoc[Components]',
        '* xref:quality-atlas/index.adoc[Quality Atlas]',
        '** xref:quality-atlas/schedule.adoc[Schedule]',
        '** xref:quality-atlas/internal.adoc[Internal]',
        '** xref:quality-atlas/portfolio.adoc[Portfolio]',
        '** xref:quality-atlas/overview.adoc[Overview]',
        '** xref:quality-atlas/quality-baseline.adoc[Quality Baseline]',
        '** xref:quality-atlas/principles.adoc[Principles]',
        '** xref:quality-atlas/architectural-dimensions.adoc[Architectural Dimensions]',
        '** xref:quality-atlas/readiness-model.adoc[Readiness Model]',
        '** xref:quality-atlas/evaluation.adoc[Evaluation]',
        '** xref:quality-atlas/glossary.adoc[Glossary]',
        '** xref:quality-atlas/explorer.adoc[Explorer]',
    ])
    write(NAV_FILE, '\n'.join(lines))


def generate_base_site() -> None:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    ensure(PAGES_DIR)
    articles = collect(ARTICLE_DIRS, allow_partials=True)
    components = load_components()
    write(OUT_DIR / 'antora.yml', 'name: ROOT\ntitle: Smart Responsor\nversion: ~\nnav:\n  - modules/ROOT/nav.adoc\n')
    write_nav()
    generate_index('article', 'Articles', 'Public articles and position papers from Smart Responsor.', articles)
    for slug, title, description in PUBLIC_SECTIONS:
        generate_index(slug, title, description, collect([DOCS_DIR / slug]))
    generate_components(components)
    write(PAGES_DIR / 'index.adoc', f'= Smart Responsor Documentation\n:description: Public portal for Smart Responsor articles, manifests, principles, glossary, and component entry points.\n\nThis is the public documentation entry point for *Smart Responsor*.\n\n* xref:article/index.adoc[Articles]\n* xref:manifest/index.adoc[Manifests]\n* xref:principle/index.adoc[Principles]\n* xref:glossary/index.adoc[Glossary]\n* xref:component/index.adoc[Components]\n\n== Snapshot\n\n* Published articles discovered from filtered source files: {len(articles)}\n* Registered components discovered from manifest: {len(components)}\n* Publication mode: clean AsciiDoc-first wave\n\nThis Antora site is generated from the current repository state.\n')


def write_owner_home_page() -> None:
    write(PAGES_DIR / 'index.adoc', '''= Oleksandr Tishchenko
:description: Owner-oriented public portal for Smartresponsor, its articles, ecosystem context, and public documentation.

This portal is the owner-oriented public entry point for *Oleksandr Tishchenko*, *Marketing America Corp*, *High Hopes*, and *Smartresponsor*.

It exists as a public layer for ideas, architecture, documentation, and strategic positioning around the systems we build and the worldview behind them.

== What Smartresponsor Means Here

Smartresponsor is not presented here as a generic AI project or as a loose collection of technical experiments.

It is approached as a long-horizon ecosystem direction: a space where product thinking, engineering discipline, protocol logic, documentation, and responsible automation are meant to converge into durable systems.

This portal therefore serves two roles at once:

* as a public-facing article and documentation space,
* and as a curated context layer for the ideas, architectural principles, and ecosystem components behind Smartresponsor.

== Core Position

A large part of the current technology conversation is too shallow.

Too much attention is concentrated on interfaces, prompts, and short-cycle novelty. Too little attention is given to structure, accountability, reproducibility, protocol design, and the quality of human thinking behind the machine layer.

The position reflected on this portal can be summarized in several core beliefs:

* AI is a stack, not just a chat interface.
* AI does not replace thinking; it reveals the quality of thinking.
* Serious automation should prefer protocol, determinism, and evidence over imitation of a human.
* Commerce and digital systems are moving toward agent-ready and protocol-ready models.
* Long-term systems need canon, continuity, and responsibility, not only speed.

== What This Portal Covers

* xref:article/index.adoc[Articles] — essays, strategic notes, technical positioning, and public reflections.
* xref:manifest/index.adoc[Manifests] — public manifest-style documents, boundary statements, and owner-level positions.
* xref:principle/index.adoc[Principles] — reusable principles and decision-interface patterns.
* xref:glossary/index.adoc[Glossary] — shared terminology for the public documentation layer.
* xref:component/index.adoc[Components] — entry points for ecosystem components and directions.
* xref:quality-atlas/index.adoc[Quality Atlas] — engineering baseline, readiness model, evaluation layer, and comparative pre-RC atlas.
* xref:about/index.adoc[About] — what this portal is and how it should be read.
* xref:owner/index.adoc[Owner] — authorship and public context.
* xref:support/index.adoc[Support] — owner-oriented support and sponsorship for documentation continuity.
* xref:contact/index.adoc[Contact] — direct owner and organizational contact page.

== Public Canon Entry Points

* xref:manifest/what-this-system-must-never-become.adoc[What This System Must Never Become]
* xref:manifest/from-punishment-to-reward.adoc[From Punishment to Reward]
* xref:principle/fact-risk-option-action-protocol.adoc[Fact, Risk, Option, Action]
* xref:principle/decision-trace.adoc[Decision Trace]
* xref:glossary/new-paradigm-glossary.adoc[New Paradigm Glossary]

== Selected Reads

* xref:article/01-human-does-not-see-reality.adoc[A Human Being Does Not See Reality. A Human Being Sees a Survival Task]
* xref:article/02-can-we-build-the-future-on-ancient-reward-system.adoc[Can We Build the Future on an Ancient Reward System?]
* xref:article/03-when-fear-becomes-the-interface.adoc[When Fear Becomes the Interface]
* xref:article/04-before-truth-the-mind-asks-are-you-one-of-us.adoc[Before Truth, the Mind Asks: Are You One of Us?]
* xref:article/05-the-inner-narrator-why-we-explain-decisions-after-they-are-made.adoc[The Inner Narrator]
* xref:article/why-the-next-e-commerce-will-not-be-a-store-with-ai.adoc[Why the Next E-Commerce Will Not Be a Store with AI]
* xref:article/odyssey-execution-control-plane.adoc[Odyssey: The Execution Control Plane for AI]
* xref:article/the-first-great-war-between-platforms-and-protocols.adoc[The First Great War Between Platforms and Protocols]

== Owner and Public Context

This site is currently maintained in owner-oriented mode.

Owner:
*Oleksandr Tishchenko*

Company:
*Marketing America Corp*

Organization:
*High Hopes*

Project / Ecosystem direction:
*Smartresponsor*

== Support

This public documentation layer is maintained directly and intentionally.

Support is tied to continuity: documentation maintenance, architectural canon, implementation notes, public context, and long-term availability of the knowledge layer around Smartresponsor.

If this portal is useful to you, see the dedicated xref:support/index.adoc[Support] page.

== Contact

For direct contact, collaboration, or owner-level communication, see xref:contact/index.adoc[Contact].
''')


def write_owner_support_pages() -> None:
    write(PAGES_DIR / 'about' / 'index.adoc', '''= About
:description: About this public documentation portal and how to use it.

This portal publishes owner-oriented documentation, essays, and ecosystem context for *Smartresponsor*.

It is designed as a public knowledge layer with practical navigation:

* xref:article/index.adoc[Articles] for long-form essays and technical thinking.
* xref:manifest/index.adoc[Manifests] for public manifest-style documents and boundary statements.
* xref:principle/index.adoc[Principles] for reusable decision-interface patterns.
* xref:glossary/index.adoc[Glossary] for shared terminology.
* xref:component/index.adoc[Components] for ecosystem structure.

For authorship context, see xref:owner/index.adoc[Owner].
''')
    write(PAGES_DIR / 'owner' / 'index.adoc', '''= Owner
:description: Owner and authorship context for this portal.

Owner and primary author:

*Oleksandr Tishchenko*

Company:

*Marketing America Corp*

Organization:

*High Hopes*

Project direction:

*Smartresponsor*

For collaboration, see xref:contact/index.adoc[Contact].
''')
    write(PAGES_DIR / 'support' / 'index.adoc', '''= Support
:description: Support options for documentation continuity and maintenance.

This portal is maintained in owner-oriented mode and updated continuously.

Support helps sustain:

* documentation maintenance,
* editorial updates,
* long-term public availability,
* architectural canon continuity.

For direct communication before support, use xref:contact/index.adoc[Contact].
''')
    write(PAGES_DIR / 'contact' / 'index.adoc', '''= Contact
:description: Contact page for owner-level communication and collaboration.

For owner-level communication, partnership, or collaboration requests:

* Owner: *Oleksandr Tishchenko*
* Company: *Marketing America Corp*
* Organization: *High Hopes*
* Project direction: *Smartresponsor*

Use the repository communication channels and official organization contacts for outreach.
''')


def write_owner_assets() -> None:
    source_dir = DOCS_DIR / 'assets' / 'images'
    target_dir = OUT_DIR / 'modules' / 'ROOT' / 'assets' / 'images'
    if source_dir.exists():
        ensure(target_dir)
        for path in source_dir.iterdir():
            if path.is_file():
                shutil.copy2(path, target_dir / path.name)


def main() -> None:
    preserved = expand_overrides(capture_component_pages(), load_slug_overrides())
    generate_base_site()
    write_owner_home_page()
    write_owner_support_pages()
    write_owner_assets()
    restore_component_pages(preserved)
    for generator in QUALITY_GENERATORS:
        subprocess.run([sys.executable, str(ROOT / 'tools' / generator)], check=True)


if __name__ == '__main__':
    main()
