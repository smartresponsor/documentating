# Current slice activation

Branch: `wave/current-slice-antora-cleanup-20260401`

This branch is activated from the current uploaded repository slice.

## Immediate focus

1. Antora-first normalization
2. MkDocs legacy evacuation
3. Mobile/sidebar navigation repair in supplemental UI
4. Preserve valuable early sources; delete only true build legacy / duplicates / noise

## Current-slice findings already confirmed

- Antora is the canonical site engine.
- `README.md` still contains stale MkDocs Material narrative.
- `.site/mkdocs.yml` still exists as legacy build contour.
- `supplemental-ui/css/owner-overrides.css` hides `.nav-panel-explore`, which is the prime suspect for the mobile sidebar issue.
