# Building the site

## Canonical build sequence

Do not run raw `npx antora antora-playbook.yml --fetch` against a stale `.antora-src/` tree.

This repository generates parts of `.antora-src/` first, including the Quality Atlas pages, and only then runs Antora.

Use one of the canonical entry points instead:

### NPM

```bash
npm run build
```

### Bash

```bash
tools/build_site.sh
```

### PowerShell

```powershell
tools/build_site.ps1
```

Equivalent manual sequence:

```bash
python3 tools/build_antora_site.py
npx antora antora-playbook.yml --fetch
```

## Why this matters

`tools/generate_quality_baseline_section.py` builds the Quality Atlas index and inserts references to `summary.adoc` and `explorer.adoc`.

`tools/generate_pre_rc_quality_atlas.py` then generates those pages into `.antora-src/`.

If you run Antora directly without rebuilding `.antora-src/` first, the site can fail with missing include or xref errors.

## CI

The GitHub Pages workflow already uses the canonical sequence.
