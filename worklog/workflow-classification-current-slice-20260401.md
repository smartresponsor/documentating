# Workflow classification — current slice

Branch: `wave/current-slice-antora-cleanup-20260401`

This document classifies publication/build workflows in the current repository slice into active, transitional, and removal-candidate groups.

## Classification principles

- **Active**: should be treated as currently meaningful in the live publication path.
- **Transitional**: still relevant for understanding the migration path or for preserving a staged rollout, but not the desired final canon.
- **Removal-candidate**: appears to be superseded, duplicated, or transitional residue that should be reviewed for deletion after verification.

## Likely active or canon-driving

### `.github/workflows/gh-pages.yml`
Status: active

Why:
- named as the canonical gh-pages writer;
- still part of the top-level build/publication story;
- should remain a primary reference point until a later consolidation commit proves otherwise.

### `.github/workflows/publish-v19-pre-rc-quality-atlas-inline-after-v17.yml`
Status: active-candidate / target canon

Why:
- cleanup canon indicates this is the intended current final publication layer.
- likely represents the newest pre-RC atlas-aware publication direction.

## Transitional but important

### `.github/workflows/antora-gh-pages-owner.yml`
Status: transitional live legacy

Why:
- cleanup canon identifies it as the current live legacy layer.
- should not be deleted blindly before the final publication chain is proven.

### `.github/workflows/publish-v17-quality-atlas-after-v16.yml`
Status: transitional

Why:
- part of atlas-related publication evolution.
- useful for migration traceability until v19 is stabilized.

### `.github/workflows/publish-v18-pre-rc-quality-atlas-after-v17.yml`
Status: transitional

Why:
- intermediate step between v17 and v19.
- likely still useful for understanding deltas in publication logic.

## Likely removal-candidates after verification

### `.github/workflows/antora-gh-pages-v2.yml`
Status: removal-candidate

### `.github/workflows/antora-gh-pages-v4.yml`
Status: removal-candidate

### `.github/workflows/antora-gh-pages-v5.yml`
Status: removal-candidate

### `.github/workflows/normalize-antora-repo-on-push.yml`
Status: removal-candidate after review

### `.github/workflows/stabilize-antora-on-push.yml`
Status: removal-candidate after review

### `.github/workflows/enable-owner-ui-on-push.yml`
Status: removal-candidate after review

### `.github/workflows/switch-owner-v2-on-push.yml`
Status: removal-candidate after review

## Immediate recommendation

1. Do not delete transitional live layers yet.
2. First prove which workflow actually owns gh-pages publication in the current slice.
3. Then collapse old `antora-gh-pages-v*` generations.
4. Only after that remove migration automations such as normalize/stabilize/switch layers if their logic is no longer needed.

## Next follow-up

The next useful artifact should classify builder scripts in the same way:
- active
- transitional
- removal-candidate
