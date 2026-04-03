# Workflow fix snippet for Quality Atlas build

## Problem

The Atlas dashboard HTML was being copied into `.site_build` too early.
Antora then rebuilt `.site_build`, so the dashboard disappeared from the final published site.

## Correct order

1. run Atlas-aware builder
2. run Antora
3. copy dashboard HTML into final `.site_build`
4. publish gh-pages

## Minimal switch

Replace the build step command:

```bash
python3 tools/build_antora_site.py
```

with:

```bash
python3 tools/build_antora_site_canonical_with_quality_atlas_embed.py
```

Then, in the `Copy public site extras` step, add:

```bash
python3 tools/publish_quality_atlas_dashboard.py
```

## Result

The final published site should contain:

- `/quality-atlas/component_quality_dashboard.html`
- embedded iframe on the `Quality Atlas` page
- nav entry for `Quality Atlas`
- home-page summary block
