# Workflow → Builder mapping matrix — current slice

Branch: `wave/current-slice-antora-cleanup-20260401`

This matrix ties together the current-slice workflow and builder classifications.
It is meant to reduce ambiguity before removing transitional publication layers.

## Matrix

| Workflow / surface | Current role | Builder linkage | Classification |
|---|---|---|---|
| `.github/workflows/gh-pages.yml` | canonical-looking gh-pages writer | currently tied to `tools/build_antora_site_v4.py` in the live repository slice | active workflow, transitional builder dependency |
| `.github/workflows/antora-gh-pages-owner.yml` | live legacy owner-facing publication layer | tied to legacy Antora publication flow | transitional live legacy |
| `.github/workflows/publish-v17-quality-atlas-after-v16.yml` | atlas evolution stage | likely tied to atlas-aware builder generation after v16 | transitional |
| `.github/workflows/publish-v18-pre-rc-quality-atlas-after-v17.yml` | pre-RC atlas evolution stage | likely tied to staged post-v17 publication logic | transitional |
| `.github/workflows/publish-v19-pre-rc-quality-atlas-inline-after-v17.yml` | intended current final publication layer | should converge toward stable facade + target canon builder arrangement | active-candidate / target canon |
| `package.json` build entry | operator-facing local build entry | points to `tools/build_antora_site.py` | active facade |
| `tools/build_antora_site.py` | stable facade | should front the desired canonical implementation | active facade |
| `tools/build_antora_site_v13.py` | intended base builder logic | desired implementation target behind facade | active-candidate / target canon |
| `tools/build_antora_site_v4.py` | live legacy builder still used by publication layer | directly referenced by current gh-pages flow in current slice | transitional live legacy |
| `tools/build_antora_site_v17.py` | atlas-aware generation bridge | relevant to v17+ publication layering | transitional |

## Key contradiction in the current slice

The current slice contains a structural contradiction:

- the operator-facing facade points to `tools/build_antora_site.py`;
- the current gh-pages writer still points to `tools/build_antora_site_v4.py`;
- cleanup canon says the intended base builder logic is `tools/build_antora_site_v13.py`;
- intended final publication direction points toward `publish-v19-pre-rc-quality-atlas-inline-after-v17.yml`.

That means the repository still has at least three simultaneous truth layers:

1. facade truth (`build_antora_site.py`)
2. live legacy publication truth (`build_antora_site_v4.py`)
3. intended base canon (`build_antora_site_v13.py`)

## Recommended consolidation order

1. Keep `tools/build_antora_site.py` as the stable public/operator entry.
2. Make workflow ownership explicit: decide which workflow is the actual final gh-pages writer.
3. Align the final gh-pages writer with the builder canon target.
4. Only then remove `v4`-dependent live legacy publication layers.
5. Collapse older `antora-gh-pages-v*` and migration automations after the final writer is proven.

## Immediate no-regret conclusion

At the current stage, the repository should be treated as:

- Antora-first in direction,
- multi-layer transitional in publication logic,
- not yet collapsed to one clean builder/workflow truth line.
