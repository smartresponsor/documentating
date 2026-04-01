# MkDocs / Material residue inventory

Branch: `wave/antora-cleanup-mobile-nav`

This inventory records confirmed and likely MkDocs/Material residues discovered during the Antora-first cleanup wave.

## Confirmed residues

### 1. `README.md`
Current narrative still says:
- build is `MkDocs Material via .site/`

Assessment:
- stale top-level repo narrative
- misleading after Antora migration
- should be rewritten, not preserved in current form

### 2. `.site/mkdocs.yml`
Confirmed legacy file.

Assessment:
- explicit MkDocs/Material build contour
- points to `../docs`
- outputs into `../.site_build`
- conflicts conceptually with Antora as the canonical engine
- safe delete candidate as build legacy

## Confirmed Antora canon evidence

- `package.json` runs Antora build flow
- `antora-playbook.yml` is canonical site playbook
- `.github/workflows/gh-pages.yml` builds and publishes Antora site
- `supplemental-ui/` is active Antora UI override layer

## Important non-residue item

### `supplemental-ui/css/owner-overrides.css`
This file is not MkDocs residue.
It is an active Antora supplemental UI override.

Assessment:
- must be patched, not evacuated
- currently hides `.nav-panel-explore`
- prime suspect for the broken mobile/sidebar navigation

## First-wave cleanup boundary

This wave should remove or correct only the following residue classes:

1. false repository narrative
2. obsolete MkDocs build contour
3. mobile-nav blocking CSS rule inside active Antora UI layer

This wave should **not** blindly remove early docs or useful source artifacts.
