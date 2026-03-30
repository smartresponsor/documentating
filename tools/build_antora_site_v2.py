#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
OUT_DIR = ROOT / ".antora-src"
PAGES_DIR = OUT_DIR / "modules" / "ROOT" / "pages"
NAV_FILE = OUT_DIR / "modules" / "ROOT" / "nav.adoc"
MANIFEST_FILE = ROOT / ".sync" / "manifest" / "component-list.yml"
ARTICLE_DIRS = [DOCS_DIR / "article", DOCS_DIR / "articles"]
DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}--?")
ATTR_RE = re.compile(r"^:([^:]+):\s*(.*)$")


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


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def slugify(value: str) -> str:
    value = DATE_PREFIX_RE.sub("", value.strip().lower())
    value = value.replace("&", " and ")
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"[^a-z0-9\-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "page"


def prettify_stem(stem: str) -> str:
    cleaned = DATE_PREFIX_RE.sub("", stem).replace("-", " ").strip()
    return cleaned.title() if cleaned else "Untitled"


def parse_front_matter(raw: str) -> tuple[dict[str, Any], str]:
    if raw.startswith("---\n"):
        parts = raw.split("\n---\n", 1)
        if len(parts) == 2:
            _, tail = parts
            header_block = raw[len("---\n") : len(raw) - len(tail) - len("\n---\n")]
            meta = yaml.safe_load(header_block) or {}
            return meta, tail
    return {}, raw


def extract_title_from_markdown(body: str) -> str:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return ""


def strip_leading_h1(body: str, title: str) -> str:
    lines = body.splitlines()
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and lines[i].strip().startswith("# "):
        current = lines[i].strip()[2:].strip()
        if current == title.strip():
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            return "\n".join(lines[i:]).lstrip()
    return body.lstrip()


def to_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def to_tags(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [to_text(v).strip() for v in value if to_text(v).strip()]
    text = to_text(value).strip()
    if not text:
        return []
    return [part.strip() for part in text.split(",") if part.strip()]


def markdown_to_asciidoc(markdown_text: str) -> str:
    result = subprocess.run(
        ["pandoc", "--from=gfm", "--to=asciidoc", "--wrap=none"],
        input=markdown_text,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


def parse_asciidoc_source(raw: str, path: Path) -> Article:
    lines = raw.splitlines()
    idx = 0
    while idx < len(lines) and not lines[idx].strip():
        idx += 1

    title = ""
    if idx < len(lines) and lines[idx].startswith("= "):
        title = lines[idx][2:].strip()
        idx += 1

    attrs: dict[str, str] = {}
    while idx < len(lines):
        line = lines[idx]
        stripped = line.strip()
        if not stripped:
            idx += 1
            break
        match = ATTR_RE.match(line)
        if not match:
            break
        attrs[match.group(1).strip().lower()] = match.group(2).strip()
        idx += 1

    body = "\n".join(lines[idx:]).lstrip()
    title = title or attrs.get("title", "") or prettify_stem(path.stem)
    slug = attrs.get("page-slug") or attrs.get("slug") or slugify(title) or slugify(path.stem)
    date = attrs.get("page-published") or attrs.get("date") or ""
    author = attrs.get("page-author") or attrs.get("author") or ""
    description = attrs.get("description", "")
    tags = to_tags(attrs.get("page-tags") or attrs.get("tags"))

    header = [f"= {title}", f":page-slug: {slug}"]
    if date:
        header.append(f":page-published: {date}")
    if author:
        header.append(f":page-author: {author}")
    if description:
        header.append(f":description: {description}")
    if tags:
        header.append(f":page-tags: {', '.join(tags)}")
    header.extend(["", f"_Source asciidoc: `{path.relative_to(ROOT).as_posix()}`_", ""])
    full_body = "\n".join(header) + body + "\n"

    return Article(
        title=title,
        slug=slug,
        date=date,
        description=description,
        author=author,
        tags=tags,
        source_rel=path.relative_to(ROOT).as_posix(),
        body_adoc=full_body,
        source_kind="adoc",
        source_rank=2,
    )


def parse_markdown_source(raw: str, path: Path) -> Article:
    meta, body = parse_front_matter(raw)
    title = to_text(meta.get("title")).strip() or extract_title_from_markdown(body) or prettify_stem(path.stem)
    slug = to_text(meta.get("slug")).strip() or slugify(title) or slugify(path.stem)
    description = to_text(meta.get("description")).strip()
    author = to_text(meta.get("author")).strip()
    date = to_text(meta.get("date")).strip().strip('"')
    tags = to_tags(meta.get("tags"))
    body = strip_leading_h1(body, title)
    body_adoc = markdown_to_asciidoc(body)

    header = [f"= {title}", f":page-slug: {slug}"]
    if date:
        header.append(f":page-published: {date}")
    if author:
        header.append(f":page-author: {author}")
    if description:
        header.append(f":description: {description}")
    if tags:
        header.append(f":page-tags: {', '.join(tags)}")
    header.extend(["", f"_Source markdown: `{path.relative_to(ROOT).as_posix()}`_", ""])
    full_body = "\n".join(header) + body_adoc + "\n"

    return Article(
        title=title,
        slug=slug,
        date=date,
        description=description,
        author=author,
        tags=tags,
        source_rel=path.relative_to(ROOT).as_posix(),
        body_adoc=full_body,
        source_kind="md",
        source_rank=1,
    )


def should_skip_source(path: Path) -> bool:
    name = path.name.lower()
    if name.startswith("_"):
        return True
    return name in {"index.md", "index.adoc", "article-template.adoc"}


def choose_better(current: Article | None, candidate: Article) -> Article:
    if current is None:
        return candidate
    current_key = (current.source_rank, current.date, current.source_rel)
    candidate_key = (candidate.source_rank, candidate.date, candidate.source_rel)
    return candidate if candidate_key > current_key else current


def collect_articles() -> list[Article]:
    discovered: dict[str, Article] = {}
    for directory in ARTICLE_DIRS:
        if not directory.exists():
            continue
        for path in sorted(directory.iterdir()):
            if not path.is_file():
                continue
            if should_skip_source(path):
                continue
            suffix = path.suffix.lower()
            if suffix not in {".md", ".adoc"}:
                continue
            raw = path.read_text(encoding="utf-8")
            article = parse_asciidoc_source(raw, path) if suffix == ".adoc" else parse_markdown_source(raw, path)
            discovered[article.slug] = choose_better(discovered.get(article.slug), article)
    return sorted(discovered.values(), key=lambda a: (a.date, a.title.lower()), reverse=True)


def load_component_manifest() -> list[tuple[str, str]]:
    if not MANIFEST_FILE.exists():
        return []
    payload = yaml.safe_load(MANIFEST_FILE.read_text(encoding="utf-8")) or {}
    components = payload.get("components") or []
    overrides = payload.get("slug_overrides") or {}
    result: list[tuple[str, str]] = []
    for name in components:
        default_slug = str(name).lower()
        slug = overrides.get(default_slug, default_slug)
        result.append((str(name), str(slug)))
    return result


def generate_article_pages(articles: list[Article]) -> None:
    index_lines = [
        "= Articles",
        ":description: Public articles and position papers from Smart Responsor.",
        "",
        "This section is the public article stream for Smart Responsor.",
        "",
        "[NOTE]",
        "====",
        "AsciiDoc is now the primary article source format. Markdown remains supported as a legacy fallback during migration.",
        "====",
        "",
        "== Latest",
        "",
    ]
    for article in articles:
        write_text(PAGES_DIR / "article" / f"{article.slug}.adoc", article.body_adoc)
        line = f"* xref:article/{article.slug}.adoc[{article.title}]"
        meta_bits = []
        if article.date:
            meta_bits.append(article.date)
        if article.source_kind:
            meta_bits.append(article.source_kind.upper())
        if article.description:
            meta_bits.append(article.description)
        if meta_bits:
            line += f" — {' — '.join(meta_bits)}"
        index_lines.append(line)
    if len(index_lines) == 12:
        index_lines.append("No published articles found yet.")
    write_text(PAGES_DIR / "article" / "index.adoc", "\n".join(index_lines))


def generate_component_pages(components: list[tuple[str, str]]) -> None:
    index_lines = [
        "= Components",
        ":description: Public entry points for Smart Responsor ecosystem components.",
        "",
        "This section is the public component map of the Smart Responsor ecosystem.",
        "",
        "== Index",
        "",
    ]
    for name, slug in components:
        index_lines.append(f"* xref:component/{slug}/index.adoc[{name}]")
        page = f"= {name}\n\nThis is the public entry page for the *{name}* component.\n\nDetailed component documentation may later be sourced from the component repository and aggregated into the portal.\n\n* Canonical slug: `{slug}`\n"
        write_text(PAGES_DIR / "component" / slug / "index.adoc", page)
    if len(index_lines) == 7:
        index_lines.append("No component registry found yet.")
    write_text(PAGES_DIR / "component" / "index.adoc", "\n".join(index_lines))


def generate_manifest_pages() -> None:
    page = "= Manifests\n:description: Canonical public manifest space for Smart Responsor.\n\nThis section is reserved for manifest-style public documents, canon notes, and owner-level statements.\n"
    write_text(PAGES_DIR / "manifest" / "index.adoc", page)


def generate_home_page(article_count: int, component_count: int) -> None:
    page = f"= Smart Responsor Documentation\n:description: Public portal for Smart Responsor articles, manifests, and component entry points.\n\nThis is the public documentation entry point for *Smart Responsor*.\n\n* xref:article/index.adoc[Articles]\n* xref:component/index.adoc[Components]\n* xref:manifest/index.adoc[Manifests]\n\n== Snapshot\n\n* Published articles discovered from source files: {article_count}\n* Registered components discovered from manifest: {component_count}\n* Article priority: AsciiDoc first, Markdown fallback\n\nThis Antora site is generated from the current repository state.\n"
    write_text(PAGES_DIR / "index.adoc", page)


def generate_nav() -> None:
    nav = "* xref:index.adoc[Home]\n* xref:article/index.adoc[Articles]\n* xref:component/index.adoc[Components]\n* xref:manifest/index.adoc[Manifests]\n"
    write_text(NAV_FILE, nav)


def generate_antora_descriptor() -> None:
    descriptor = "name: ROOT\ntitle: Smart Responsor\nversion: ~\nnav:\n  - modules/ROOT/nav.adoc\n"
    write_text(OUT_DIR / "antora.yml", descriptor)


def main() -> None:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    ensure_dir(PAGES_DIR)
    articles = collect_articles()
    components = load_component_manifest()
    generate_antora_descriptor()
    generate_nav()
    generate_article_pages(articles)
    generate_component_pages(components)
    generate_manifest_pages()
    generate_home_page(article_count=len(articles), component_count=len(components))


if __name__ == "__main__":
    main()
