#!/usr/bin/env python3
from __future__ import annotations

"""Canonical Antora builder for the current publication contract.

This builder owns the full canonical generation line directly.
It generates the base Antora content tree, applies the canonical
owner-facing home page, preserves component report/detail pages across
regeneration, expands slug overrides, and then generates the Quality Atlas
baseline section and the pre-RC Quality Atlas comparative layer.
"""

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / 'docs'
OUT_DIR = ROOT / '.antora-src'
PAGES_DIR = OUT_DIR / 'modules' / 'ROOT' / 'pages'
COMPONENT_DIR = PAGES_DIR / 'component'
NAV_FILE = OUT_DIR / 'modules' / 'ROOT' / 'nav.adoc'
MANIFEST_FILE = ROOT / '.sync' / 'manifest' / 'component-list.yml'
ARTICLE_DIRS = [DOCS_DIR / 'article']
DATE_PREFIX_RE = re.compile(r'^\d{4}-\d{2}-\d{2}--?')
ATTR_RE = re.compile(r'^:([^:]+):\s*(.*)$')
ASSET_IMAGE_RE = re.compile(r'image::/assets/([^\[]+)\[')
SKIP_RELS = {
    'docs/article/2026-03-29-ai-is-not-just-chatgpt-five-layer-stack.adoc',
    'docs/article/2026-03-29-ai-ne-zamenyaet-myshlenie-obnazhaet-kachestvo.adoc',
    'docs/article/odyssey-who-is-announcement.adoc',
}
SKIP_SLUGS = {'tesr', 'test'}


@dataclass
class Article:
    title: str
    slug: str
    date: str
    description: str
    author: str
    tags: list[str]
    source_rel: str
    body_adoc: str
    source_kind: str
    source_rank: int


def ensure(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write(path: Path, content: str) -> None:
    ensure(path.parent)
    path.write_text(content.rstrip() + '\n', encoding='utf-8')


def non_ascii(value: str) -> bool:
    return any(ord(ch) > 127 for ch in value)


def slugify(value: str) -> str:
    value = DATE_PREFIX_RE.sub('', value.strip().lower())
    value = value.replace('&', ' and ')
    value = re.sub(r'[\s_]+', '-', value)
    value = re.sub(r'[^a-z0-9\-]+', '-', value)
    value = re.sub(r'-{2,}', '-', value).strip('-')
    return value or 'page'


def norm(value: str) -> str:
    return re.sub(r'[^a-z0-9]+', '', slugify(value))


def tags_of(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [part.strip() for part in str(value).split(',') if part.strip()]


def md_to_adoc(text: str) -> str:
    return subprocess.run(
        ['pandoc', '--from=gfm', '--to=asciidoc', '--wrap=none'],
        input=text,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()


def normalize_asset_image_paths(text: str) -> str:
    return ASSET_IMAGE_RE.sub(r'image::\1[', text)


def derive_slug(explicit: str, title: str, path: Path) -> str:
    if explicit.strip():
        return explicit.strip()
    title_slug = slugify(title)
    path_slug = slugify(path.stem)
    if title_slug in {'page', 'chatgpt', 'article', 'post'} and path_slug not in {'page', title_slug}:
        return path_slug
    if non_ascii(title) and path_slug not in {'page'} and len(path_slug) >= 8:
        return path_slug
    return path_slug if title_slug == 'page' and path_slug != 'page' else title_slug


def parse_adoc(raw: str, path: Path) -> Article:
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
    body = normalize_asset_image_paths('\n'.join(lines[i:]).lstrip())
    title = title or attrs.get('title', '') or path.stem
    slug = derive_slug(attrs.get('page-slug', '') or attrs.get('slug', ''), title, path)
    date = attrs.get('page-published') or attrs.get('date') or ''
    author = attrs.get('page-author') or attrs.get('author') or ''
    desc = attrs.get('description', '')
    tags = tags_of(attrs.get('page-tags') or attrs.get('tags'))
    head = [f'= {title}', f':page-slug: {slug}']
    if date:
        head.append(f':page-published: {date}')
    if author:
        head.append(f':page-author: {author}')
    if desc:
        head.append(f':description: {desc}')
    if tags:
        head.append(f":page-tags: {', '.join(tags)}")
    head.extend(['', f"_Source asciidoc: `{path.relative_to(ROOT).as_posix()}`_", ''])
    return Article(title, slug, date, desc, author, tags, path.relative_to(ROOT).as_posix(), '\n'.join(head) + body + '\n', 'adoc', 2)


def parse_md(raw: str, path: Path) -> Article:
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
    slug = derive_slug(str(meta.get('slug', '')).strip(), title, path)
    desc = str(meta.get('description', '')).strip()
    author = str(meta.get('author', '')).strip()
    date = str(meta.get('date', '')).strip().strip('"')
    tags = tags_of(meta.get('tags'))
    lines = body.splitlines()
    j = 0
    while j < len(lines) and not lines[j].strip():
        j += 1
    if j < len(lines) and lines[j].strip().startswith('# ') and lines[j].strip()[2:].strip() == title:
        body = '\n'.join(lines[j + 1 :]).lstrip()
    head = [f'= {title}', f':page-slug: {slug}']
    if date:
        head.append(f':page-published: {date}')
    if author:
        head.append(f':page-author: {author}')
    if desc:
        head.append(f':description: {desc}')
    if tags:
        head.append(f":page-tags: {', '.join(tags)}")
    head.extend(['', f"_Source markdown: `{path.relative_to(ROOT).as_posix()}`_", ''])
    return Article(
        title,
        slug,
        date,
        desc,
        author,
        tags,
        path.relative_to(ROOT).as_posix(),
        '\n'.join(head) + normalize_asset_image_paths(md_to_adoc(body)) + '\n',
        'md',
        1,
    )


def skip(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    name = path.name.lower()
    return rel in SKIP_RELS or name.startswith('_') or name in {'index.md', 'index.adoc', 'article-template.adoc'}


def choose(current: Article | None, candidate: Article) -> Article:
    if current is None:
        return candidate
    return candidate if (candidate.source_rank, candidate.date, candidate.source_rel) > (current.source_rank, current.date, current.source_rel) else current


def collect_articles() -> list[Article]:
    found: dict[str, Article] = {}
    adoc_titles: set[str] = set()
    adoc_slugs: set[str] = set()
    for directory in ARTICLE_DIRS:
        if not directory.exists():
            continue
        for path in sorted(directory.iterdir()):
            if not path.is_file() or skip(path) or path.suffix.lower() != '.adoc':
                continue
            article = parse_adoc(path.read_text(encoding='utf-8'), path)
            if article.slug in SKIP_SLUGS or norm(article.title) == 'tesr':
                continue
            found[article.slug] = choose(found.get(article.slug), article)
            adoc_titles.add(norm(article.title))
            adoc_slugs.add(norm(article.slug))
    for directory in ARTICLE_DIRS:
        if not directory.exists():
            continue
        for path in sorted(directory.iterdir()):
            if not path.is_file() or skip(path) or path.suffix.lower() != '.md':
                continue
            article = parse_md(path.read_text(encoding='utf-8'), path)
            if article.slug in SKIP_SLUGS or norm(article.title) == 'tesr':
                continue
            if norm(article.title) in adoc_titles or norm(article.slug) in adoc_slugs:
                continue
            found[article.slug] = choose(found.get(article.slug), article)
    return sorted(found.values(), key=lambda article: (article.date, article.title.lower()), reverse=True)


def load_components() -> list[tuple[str, str]]:
    if not MANIFEST_FILE.exists():
        return []
    payload = yaml.safe_load(MANIFEST_FILE.read_text(encoding='utf-8')) or {}
    components = payload.get('components') or []
    overrides = payload.get('slug_overrides') or {}
    return [(str(name), str(overrides.get(str(name).lower(), str(name).lower()))) for name in components]


def load_slug_overrides() -> dict[str, str]:
    if not MANIFEST_FILE.exists():
        return {}
    payload = yaml.safe_load(MANIFEST_FILE.read_text(encoding='utf-8')) or {}
    raw = payload.get('slug_overrides') or {}
    return {str(key): str(value) for key, value in raw.items()}


def capture_component_pages() -> dict[str, bytes]:
    preserved: dict[str, bytes] = {}
    if not COMPONENT_DIR.exists():
        return preserved
    for path in COMPONENT_DIR.rglob('*'):
        if not path.is_file():
            continue
        rel = path.relative_to(COMPONENT_DIR).as_posix()
        if rel == 'index.adoc':
            continue
        preserved[rel] = path.read_bytes()
    return preserved


def expand_with_slug_overrides(preserved: dict[str, bytes], overrides: dict[str, str]) -> dict[str, bytes]:
    expanded = dict(preserved)
    for source_slug, target_slug in overrides.items():
        source_prefix = f'{source_slug}/'
        target_prefix = f'{target_slug}/'
        for rel, payload in list(preserved.items()):
            if rel.startswith(source_prefix):
                expanded[target_prefix + rel[len(source_prefix):]] = payload
    return expanded


def restore_component_pages(preserved: dict[str, bytes]) -> None:
    for rel, payload in preserved.items():
        target = COMPONENT_DIR / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)


def generate_articles(articles: list[Article]) -> None:
    lines = [
        '= Articles',
        ':description: Public articles and position papers from Smart Responsor.',
        '',
        'This section is the public article stream for Smart Responsor.',
        '',
        '[NOTE]',
        '====',
        'AsciiDoc is the canonical article source format. Legacy duplicates and noisy source artifacts are filtered out during publication.',
        '====',
        '',
        '== Latest',
        '',
    ]
    for article in articles:
        write(PAGES_DIR / 'article' / f'{article.slug}.adoc', article.body_adoc)
        meta = [article.date] if article.date else []
        meta.append(article.source_kind.upper())
        if article.description:
            meta.append(article.description)
        suffix = f" — {' — '.join(meta)}" if meta else ''
        lines.append(f'* xref:article/{article.slug}.adoc[{article.title}]{suffix}')
    if len(lines) == 12:
        lines.append('No published articles found yet.')
    write(PAGES_DIR / 'article' / 'index.adoc', '\n'.join(lines))


def generate_components(components: list[tuple[str, str]]) -> None:
    lines = [
        '= Components',
        ':description: Public entry points for Smart Responsor ecosystem components.',
        '',
        'This section is the public component map of the Smart Responsor ecosystem.',
        '',
        '== Index',
        '',
    ]
    for name, slug in components:
        lines.append(f'* xref:component/{slug}/index.adoc[{name}]')
        write(
            PAGES_DIR / 'component' / slug / 'index.adoc',
            f"= {name}\n\nThis is the public entry page for the *{name}* component.\n\nDetailed component documentation may later be sourced from the component repository and aggregated into the portal.\n\n* Canonical slug: `{slug}`\n",
        )
    if len(lines) == 7:
        lines.append('No component registry found yet.')
    write(PAGES_DIR / 'component' / 'index.adoc', '\n'.join(lines))


def generate_base_site() -> None:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    ensure(PAGES_DIR)
    articles = collect_articles()
    components = load_components()
    write(OUT_DIR / 'antora.yml', 'name: ROOT\ntitle: Smart Responsor\nversion: ~\nnav:\n  - modules/ROOT/nav.adoc\n')
    write(NAV_FILE, '* xref:index.adoc[Home]\n* xref:article/index.adoc[Articles]\n* xref:component/index.adoc[Components]\n* xref:manifest/index.adoc[Manifests]\n')
    generate_articles(articles)
    generate_components(components)
    write(
        PAGES_DIR / 'manifest' / 'index.adoc',
        '= Manifests\n:description: Canonical public manifest space for Smart Responsor.\n\nThis section is reserved for manifest-style public documents, canon notes, and owner-level statements.\n',
    )
    write(
        PAGES_DIR / 'index.adoc',
        f"= Smart Responsor Documentation\n:description: Public portal for Smart Responsor articles, manifests, and component entry points.\n\nThis is the public documentation entry point for *Smart Responsor*.\n\n* xref:article/index.adoc[Articles]\n* xref:component/index.adoc[Components]\n* xref:manifest/index.adoc[Manifests]\n\n== Snapshot\n\n* Published articles discovered from filtered source files: {len(articles)}\n* Registered components discovered from manifest: {len(components)}\n* Publication mode: clean AsciiDoc-first wave\n\nThis Antora site is generated from the current repository state.\n",
    )


def write_owner_home_page() -> None:
    (PAGES_DIR / 'index.adoc').write_text(
        '''= Oleksandr Tishchenko
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
* xref:component/index.adoc[Components] — entry points for ecosystem components and directions.
* xref:manifest/index.adoc[Manifests] — canon, principles, and owner-level statements.
* xref:about/index.adoc[About] — what this portal is and how it should be read.
* xref:owner/index.adoc[Owner] — authorship and public context.
* xref:support/index.adoc[Support] — owner-oriented support and sponsorship for documentation continuity.
* xref:contact/index.adoc[Contact] — direct owner and organizational contact page.

== Why These Articles Matter

Not every article on this portal is narrowly about Smartresponsor itself. Some are wider essays about AI, engineering, labor, cognition, systems, and platform dynamics.

But together they reveal the same center of gravity:

* a preference for systems over noise,
* a preference for architecture over hype,
* a preference for durable structure over disposable acceleration,
* and a preference for responsible execution over performative automation.

That is why this portal should be read not only as a blog, but as a public map of intent.

== Selected Themes

* AI as industrial and infrastructural stack rather than surface-level conversation.
* Cognition, decomposition, and verification as the real bottlenecks of productive AI use.
* Execution control, evidence, and accountability in agent-oriented systems.
* Protocol-first commerce and machine-readable system design.
* Public documentation as part of long-term technical continuity, not as afterthought.

== Selected Reads

* xref:article/ai-is-not-just-chatgpt-five-layer-stack.adoc[AI Is Not Just ChatGPT]
* xref:article/ai-does-not-replace-thinking-it-reveals-its-quality.adoc[AI Does Not Replace Thinking. It Reveals Its Quality.]
* xref:article/do-not-scale-the-imitation-of-a-human.adoc[Do Not Scale the Imitation of a Human]
* xref:article/why-the-next-e-commerce-will-not-be-a-store-with-ai.adoc[Why the Next E-Commerce Will Not Be a Store with AI]
* xref:article/odyssey-execution-control-plane.adoc[Odyssey: The Execution Control Plane for AI]
* xref:article/the-first-great-war-between-platforms-and-protocols.adoc[The First Great War Between Platforms and Protocols]

== Owner and Public Context

This site is currently maintained in an owner-oriented mode.

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
''',
        encoding='utf-8',
    )


def write_owner_support_pages() -> None:
    write(
        PAGES_DIR / 'about' / 'index.adoc',
        '''= About
:description: About this public documentation portal and how to use it.

This portal publishes owner-oriented documentation, essays, and ecosystem context for *Smartresponsor*.

It is designed as a public knowledge layer with practical navigation:

* xref:article/index.adoc[Articles] for long-form essays and technical thinking.
* xref:component/index.adoc[Components] for ecosystem structure.
* xref:manifest/index.adoc[Manifests] for canon and principles.

For authorship context, see xref:owner/index.adoc[Owner].
''',
    )
    write(
        PAGES_DIR / 'owner' / 'index.adoc',
        '''= Owner
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
''',
    )
    write(
        PAGES_DIR / 'support' / 'index.adoc',
        '''= Support
:description: Support options for documentation continuity and maintenance.

This portal is maintained in owner-oriented mode and updated continuously.

Support helps sustain:

* documentation maintenance,
* editorial updates,
* long-term public availability,
* architectural canon continuity.

For direct communication before support, use xref:contact/index.adoc[Contact].
''',
    )
    write(
        PAGES_DIR / 'contact' / 'index.adoc',
        '''= Contact
:description: Contact page for owner-level communication and collaboration.

For owner-level communication, partnership, or collaboration requests:

* Owner: *Oleksandr Tishchenko*
* Company: *Marketing America Corp*
* Organization: *High Hopes*
* Project direction: *Smartresponsor*

Use the repository communication channels and official organization contacts for outreach.
''',
    )


def write_owner_assets() -> None:
    source_dir = DOCS_DIR / 'assets' / 'images'
    target_dir = OUT_DIR / 'modules' / 'ROOT' / 'assets' / 'images'
    if source_dir.exists():
        ensure(target_dir)
        for path in source_dir.iterdir():
            if path.is_file():
                shutil.copy2(path, target_dir / path.name)


def main() -> None:
    slug_overrides = load_slug_overrides()
    preserved_component_pages = expand_with_slug_overrides(capture_component_pages(), slug_overrides)
    generate_base_site()
    write_owner_home_page()
    write_owner_support_pages()
    write_owner_assets()
    restore_component_pages(preserved_component_pages)
    subprocess.run(['python3', str(ROOT / 'tools' / 'generate_quality_baseline_section.py')], check=True)
    subprocess.run(['python3', str(ROOT / 'tools' / 'generate_pre_rc_quality_atlas.py')], check=True)


if __name__ == '__main__':
    main()
