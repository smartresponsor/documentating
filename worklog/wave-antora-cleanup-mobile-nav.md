# Wave: Antora cleanup + mobile nav

Branch: `wave/antora-cleanup-mobile-nav`

## Goals

1. Evacuate MkDocs/Material legacy where it is only build contour and not a valuable source.
2. Preserve and re-home useful early sources instead of deleting them blindly.
3. Normalize repository narrative so Antora is the single source of truth.
4. Fix mobile/sidebar navigation in the Antora UI override layer.
5. Keep wave scope tight and avoid format churn.

## Confirmed findings

- Canonical site engine is Antora.
- `README.md` still describes MkDocs Material and is out of date.
- Legacy file `.site/mkdocs.yml` still exists and should be evacuated.
- `supplemental-ui/css/owner-overrides.css` hides `.nav-panel-explore`, which is a prime suspect for the mobile sidebar problem.

## First-wave target changes

- Rewrite `README.md` to Antora-first wording.
- Remove `.site/mkdocs.yml`.
- Stop hiding `.nav-panel-explore` in `supplemental-ui/css/owner-overrides.css`.
- Re-scan for other MkDocs/Material leftovers after the first wave lands.

## Preservation rule

Before deleting any legacy artifact, classify it as one of:

- publishable doc
- source-for-doc
- code/tooling
- build legacy
- duplicate/noise

Only build legacy and duplicate/noise are safe delete candidates by default.
