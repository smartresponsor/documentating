# Current slice focus: builder and workflow canon

Branch: `wave/current-slice-antora-cleanup-20260401`

## Why this wave moved away from README/CSS

The current repository slice shows a larger structural problem:
- many generations of Antora publish workflows are still present;
- multiple builder versions still coexist;
- cleanup manifests already acknowledge that the repository is in a transition state rather than one stable canon.

Because of that, the next high-value work should focus on builder/workflow truth layers before cosmetic or narrow UI cleanup.

## Confirmed current-slice facts

- `package.json` builds through `tools/build_antora_site.py`
- `.github/workflows/gh-pages.yml` still builds through `tools/build_antora_site_v4.py`
- cleanup canon says intended base builder logic is `tools/build_antora_site_v13.py`
- cleanup canon says current live legacy builder is `tools/build_antora_site_v4.py`
- current intended final publish layer is `publish-v19-pre-rc-quality-atlas-inline-after-v17.yml`
- current live legacy layer is `antora-gh-pages-owner.yml`

## Productive next-wave target

1. Normalize builder canon:
   - decide whether `tools/build_antora_site_v13.py` should become the real canonical base;
   - preserve `tools/build_antora_site_v4.py` until publication chain is proven stable;
   - mark older builder generations as review/remove candidates.

2. Normalize workflow canon:
   - classify active, transitional, and removal-candidate workflow files;
   - identify which workflow is the actual gh-pages writer;
   - collapse publish layering only after that is proven.

3. Keep atlas path explicit:
   - preserve pre-RC atlas generator direction;
   - avoid deleting atlas-related transitional layers before the final writer is confirmed.

## Files that now look more strategically important than README/CSS

- `.cleanup/publication-canon-2026-03-31.yml`
- `.cleanup/removal-candidates-2026-03-31.yml`
- `report/documentating-cleanup-audit-2026-03-31.adoc`
- `tools/build_antora_site.py`
- `tools/build_antora_site_v4.py`
- `tools/build_antora_site_v13.py`
- `tools/build_antora_site_v17.py`
- `.github/workflows/gh-pages.yml`
- `.github/workflows/antora-gh-pages-owner.yml`
- `.github/workflows/publish-v17-quality-atlas-after-v16.yml`
- `.github/workflows/publish-v18-pre-rc-quality-atlas-after-v17.yml`
- `.github/workflows/publish-v19-pre-rc-quality-atlas-inline-after-v17.yml`

## Recommendation

The next real cleanup/development wave should be a builder/workflow consolidation wave, not a surface-only wave.
