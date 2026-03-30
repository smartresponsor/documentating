#!/usr/bin/env python3
from __future__ import annotations
import re, shutil, subprocess
from dataclasses import dataclass
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / 'docs'
OUT_DIR = ROOT / '.antora-src'
PAGES_DIR = OUT_DIR / 'modules' / 'ROOT' / 'pages'
NAV_FILE = OUT_DIR / 'modules' / 'ROOT' / 'nav.adoc'
MANIFEST_FILE = ROOT / '.sync' / 'manifest' / 'component-list.yml'
ARTICLE_DIRS = [DOCS_DIR / 'article', DOCS_DIR / 'articles']
DATE_PREFIX_RE = re.compile(r'^\d{4}-\d{2}-\d{2}--?')
ATTR_RE = re.compile(r'^:([^:]+):\s*(.*)$')
SKIP_RELS = {
    'docs/article/2026-03-29-ai-is-not-just-chatgpt-five-layer-stack.adoc',
    'docs/article/2026-03-29-ai-ne-zamenyaet-myshlenie-obnazhaet-kachestvo.adoc',
    'docs/article/odyssey-who-is-announcement.adoc',
    'docs/article/2026-03-29--tesr.md',
    'docs/article/2026-03-29--2026-03-29-technological-inequality-2-0-cognitive-divide.md',
    'docs/article/odyssey-who-is-announcement.md',
    'docs/article/2026-03-29--why-the-next-e-commerce-will-not-be-a-store-with-ai.md',
    'docs/articles/2026-03-29-the-first-great-war-between-platforms-and-protocols.md',
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

def ensure(path: Path): path.mkdir(parents=True, exist_ok=True)
def write(path: Path, content: str): ensure(path.parent); path.write_text(content.rstrip() + '\n', encoding='utf-8')
def non_ascii(s: str) -> bool: return any(ord(ch) > 127 for ch in s)

def slugify(value: str) -> str:
    value = DATE_PREFIX_RE.sub('', value.strip().lower())
    value = value.replace('&', ' and ')
    value = re.sub(r'[\s_]+', '-', value)
    value = re.sub(r'[^a-z0-9\-]+', '-', value)
    value = re.sub(r'-{2,}', '-', value).strip('-')
    return value or 'page'

def norm(value: str) -> str: return re.sub(r'[^a-z0-9]+', '', slugify(value))
def tags_of(value):
    if value is None: return []
    if isinstance(value, list): return [str(v).strip() for v in value if str(v).strip()]
    return [p.strip() for p in str(value).split(',') if p.strip()]

def md_to_adoc(text: str) -> str:
    return subprocess.run(['pandoc','--from=gfm','--to=asciidoc','--wrap=none'], input=text, text=True, capture_output=True, check=True).stdout.strip()

def derive_slug(explicit: str, title: str, path: Path) -> str:
    if explicit.strip(): return explicit.strip()
    t = slugify(title)
    p = slugify(path.stem)
    if t in {'page','chatgpt','article','post'} and p not in {'page', t}: return p
    if non_ascii(title) and p not in {'page'} and len(p) >= 8: return p
    return p if t == 'page' and p != 'page' else t

def parse_adoc(raw: str, path: Path) -> Article:
    lines = raw.splitlines(); i = 0
    while i < len(lines) and not lines[i].strip(): i += 1
    title = ''
    if i < len(lines) and lines[i].startswith('= '): title = lines[i][2:].strip(); i += 1
    attrs = {}
    while i < len(lines):
        m = ATTR_RE.match(lines[i])
        if not m: break
        attrs[m.group(1).strip().lower()] = m.group(2).strip(); i += 1
        if i < len(lines) and not lines[i].strip(): i += 1; break
    body = '\n'.join(lines[i:]).lstrip()
    title = title or attrs.get('title','') or path.stem
    slug = derive_slug(attrs.get('page-slug','') or attrs.get('slug',''), title, path)
    date = attrs.get('page-published') or attrs.get('date') or ''
    author = attrs.get('page-author') or attrs.get('author') or ''
    desc = attrs.get('description','')
    tags = tags_of(attrs.get('page-tags') or attrs.get('tags'))
    head = [f'= {title}', f':page-slug: {slug}']
    if date: head.append(f':page-published: {date}')
    if author: head.append(f':page-author: {author}')
    if desc: head.append(f':description: {desc}')
    if tags: head.append(f":page-tags: {', '.join(tags)}")
    head.extend(['', f"_Source asciidoc: `{path.relative_to(ROOT).as_posix()}`_", ''])
    return Article(title, slug, date, desc, author, tags, path.relative_to(ROOT).as_posix(), '\n'.join(head) + body + '\n', 'adoc', 2)

def parse_md(raw: str, path: Path) -> Article:
    meta, body = ({}, raw)
    if raw.startswith('---\n') and '\n---\n' in raw:
        left, body = raw.split('\n---\n', 1)
        meta = yaml.safe_load(left[4:]) or {}
    title = str(meta.get('title','')).strip()
    if not title:
        for line in body.splitlines():
            if line.strip().startswith('# '): title = line.strip()[2:].strip(); break
    title = title or path.stem
    slug = derive_slug(str(meta.get('slug','')).strip(), title, path)
    desc = str(meta.get('description','')).strip(); author = str(meta.get('author','')).strip(); date = str(meta.get('date','')).strip().strip('"')
    tags = tags_of(meta.get('tags'))
    lines = body.splitlines(); j = 0
    while j < len(lines) and not lines[j].strip(): j += 1
    if j < len(lines) and lines[j].strip().startswith('# ') and lines[j].strip()[2:].strip() == title: body = '\n'.join(lines[j+1:]).lstrip()
    head = [f'= {title}', f':page-slug: {slug}']
    if date: head.append(f':page-published: {date}')
    if author: head.append(f':page-author: {author}')
    if desc: head.append(f':description: {desc}')
    if tags: head.append(f":page-tags: {', '.join(tags)}")
    head.extend(['', f"_Source markdown: `{path.relative_to(ROOT).as_posix()}`_", ''])
    return Article(title, slug, date, desc, author, tags, path.relative_to(ROOT).as_posix(), '\n'.join(head) + md_to_adoc(body) + '\n', 'md', 1)

def skip(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix(); name = path.name.lower()
    return rel in SKIP_RELS or name.startswith('_') or name in {'index.md','index.adoc','article-template.adoc'}

def choose(cur, cand):
    if cur is None: return cand
    return cand if (cand.source_rank, cand.date, cand.source_rel) > (cur.source_rank, cur.date, cur.source_rel) else cur

def collect_articles() -> list[Article]:
    found = {}; adoc_titles = set(); adoc_slugs = set()
    for d in ARTICLE_DIRS:
        if not d.exists(): continue
        for p in sorted(d.iterdir()):
            if not p.is_file() or skip(p) or p.suffix.lower() != '.adoc': continue
            a = parse_adoc(p.read_text(encoding='utf-8'), p)
            if a.slug in SKIP_SLUGS or norm(a.title) == 'tesr': continue
            found[a.slug] = choose(found.get(a.slug), a); adoc_titles.add(norm(a.title)); adoc_slugs.add(norm(a.slug))
    for d in ARTICLE_DIRS:
        if not d.exists(): continue
        for p in sorted(d.iterdir()):
            if not p.is_file() or skip(p) or p.suffix.lower() != '.md': continue
            a = parse_md(p.read_text(encoding='utf-8'), p)
            if a.slug in SKIP_SLUGS or norm(a.title) == 'tesr': continue
            if norm(a.title) in adoc_titles or norm(a.slug) in adoc_slugs: continue
            found[a.slug] = choose(found.get(a.slug), a)
    return sorted(found.values(), key=lambda a: (a.date, a.title.lower()), reverse=True)

def load_components():
    if not MANIFEST_FILE.exists(): return []
    payload = yaml.safe_load(MANIFEST_FILE.read_text(encoding='utf-8')) or {}
    comps = payload.get('components') or []; overrides = payload.get('slug_overrides') or {}
    return [(str(name), str(overrides.get(str(name).lower(), str(name).lower()))) for name in comps]

def generate_articles(articles: list[Article]):
    lines = ['= Articles', ':description: Public articles and position papers from Smart Responsor.', '', 'This section is the public article stream for Smart Responsor.', '', '[NOTE]', '====', 'AsciiDoc is the canonical article source format. Legacy duplicates and noisy source artifacts are filtered out during publication.', '====', '', '== Latest', '']
    for a in articles:
        write(PAGES_DIR / 'article' / f'{a.slug}.adoc', a.body_adoc)
        meta = [a.date] if a.date else []; meta.append(a.source_kind.upper())
        if a.description: meta.append(a.description)
        suffix = f" — {' — '.join(meta)}" if meta else ''
        lines.append(f"* xref:article/{a.slug}.adoc[{a.title}]{suffix}")
    if len(lines) == 12: lines.append('No published articles found yet.')
    write(PAGES_DIR / 'article' / 'index.adoc', '\n'.join(lines))

def generate_components(components):
    lines = ['= Components', ':description: Public entry points for Smart Responsor ecosystem components.', '', 'This section is the public component map of the Smart Responsor ecosystem.', '', '== Index', '']
    for name, slug in components:
        lines.append(f'* xref:component/{slug}/index.adoc[{name}]')
        write(PAGES_DIR / 'component' / slug / 'index.adoc', f"= {name}\n\nThis is the public entry page for the *{name}* component.\n\nDetailed component documentation may later be sourced from the component repository and aggregated into the portal.\n\n* Canonical slug: `{slug}`\n")
    if len(lines) == 7: lines.append('No component registry found yet.')
    write(PAGES_DIR / 'component' / 'index.adoc', '\n'.join(lines))

def main():
    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    ensure(PAGES_DIR)
    articles = collect_articles(); components = load_components()
    write(OUT_DIR / 'antora.yml', 'name: ROOT\ntitle: Smart Responsor\nversion: ~\nnav:\n  - modules/ROOT/nav.adoc\n')
    write(NAV_FILE, '* xref:index.adoc[Home]\n* xref:article/index.adoc[Articles]\n* xref:component/index.adoc[Components]\n* xref:manifest/index.adoc[Manifests]\n')
    generate_articles(articles); generate_components(components)
    write(PAGES_DIR / 'manifest' / 'index.adoc', '= Manifests\n:description: Canonical public manifest space for Smart Responsor.\n\nThis section is reserved for manifest-style public documents, canon notes, and owner-level statements.\n')
    write(PAGES_DIR / 'index.adoc', f"= Smart Responsor Documentation\n:description: Public portal for Smart Responsor articles, manifests, and component entry points.\n\nThis is the public documentation entry point for *Smart Responsor*.\n\n* xref:article/index.adoc[Articles]\n* xref:component/index.adoc[Components]\n* xref:manifest/index.adoc[Manifests]\n\n== Snapshot\n\n* Published articles discovered from filtered source files: {len(articles)}\n* Registered components discovered from manifest: {len(components)}\n* Publication mode: clean AsciiDoc-first wave\n\nThis Antora site is generated from the current repository state.\n")

if __name__ == '__main__':
    main()
