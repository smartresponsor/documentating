# Repository manifest

## Product (static content)

- docs/ — documentation and article sources (Markdown and AsciiDoc)
- doc/ — editorial/article staging surface retained in the repository
- assets/ — canonical images, diagrams, and static attachments

## Runtime (build/sync/deploy)

- .antora-src/ — generated Antora source tree
- .sync/ — collectors and manifests for aggregating docs from component repositories
- .deploy/ — deployment packaging and environment templates
- .github/ — CI/workflows (single canonical GitHub Pages publish owner)
- supplemental-ui/ — Antora supplemental UI overrides
- tools/ — canonical build helper and supporting atlas generators
- report/ — cleanup audit and related repository reports

## Canonical contract

- build entry: `tools/build_antora_site.py`
- publish owner: `.github/workflows/gh-pages.yml`
- playbook: `antora-playbook.yml`
- asset source: `assets/`

## RAG

See `RAG_SOURCES.md` for what should be indexed by local memory tooling.
