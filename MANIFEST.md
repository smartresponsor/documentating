# Repository manifest

## Product (static content)

- content/ — Markdown content (public documentation and articles)
- asset/ — images/diagrams (static attachments)

## Runtime (build/sync/deploy)

- .site/ — MkDocs Material config (build runtime)
- .sync/ — collectors and manifests for aggregating docs from component repositories
- .patch/ — rare overlays (exceptions)
- deploy/ — deployment methods (optional; GitHub Pages is in .github/workflows)
- tool/ — verification/smoke utilities
- .github/ — CI/workflows (GitHub Pages build+deploy)

## RAG

See `RAG_SOURCES.md` for what should be indexed by local memory tooling.
