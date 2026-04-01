# Builder classification — current slice

Branch: `wave/current-slice-antora-cleanup-20260401`

This document classifies Antora site builder scripts in the current repository slice into active, transitional, and removal-candidate groups.

## Classification principles

- **Active**: should be treated as a current truth layer in the build/publication path.
- **Transitional**: still useful for staged migration, auditability, or fallback during cleanup.
- **Removal-candidate**: appears superseded, duplicated, or no longer desirable as part of the long-term canon.

## Likely active or canon-driving

### `tools/build_antora_site.py`
Status: active facade

Why:
- exposed as the top-level builder entry in `package.json`;
- should remain the stable operator-facing entry point even if its internals later switch to a newer implementation.

### `tools/build_antora_site_v13.py`
Status: active-candidate / intended base canon

Why:
- cleanup canon indicates that intended base builder logic is now `v13`.
- this makes it the strongest candidate for the real implementation target behind the stable facade.

## Transitional but important

### `tools/build_antora_site_v4.py`
Status: transitional live legacy

Why:
- current gh-pages workflow still points to `v4`.
- cannot be removed before the publication writer is updated and verified.

### `tools/build_antora_site_v17.py`
Status: transitional atlas-aware builder

Why:
- the repository contains atlas/pre-RC publication layering after `v17`.
- likely still useful as a migration bridge or reference point for publication behavior.

## Possible review targets

### `tools/build_antora_site_v2.py`
Status: review / likely removal-candidate

Why:
- appears to belong to an earlier transition generation.
- should be removable once no active workflow or staged migration depends on it.

### Other older numbered builder generations
Status: review / likely removal-candidate

Why:
- if not referenced by active workflows, audit files, or reproducibility needs, they should not stay indefinitely in the canonical surface.

## Immediate recommendation

1. Keep `tools/build_antora_site.py` as the stable facade.
2. Decide whether it should wrap or mirror `tools/build_antora_site_v13.py`.
3. Preserve `tools/build_antora_site_v4.py` until the real gh-pages writer no longer depends on it.
4. Preserve `tools/build_antora_site_v17.py` until atlas/pre-RC publication layers are fully consolidated.
5. Review older generations only after builder-to-workflow mapping is fully explicit.

## Next follow-up

The next useful artifact should be a mapping matrix:
- workflow -> builder
- workflow -> publication role
- builder -> live / transitional / target canon
