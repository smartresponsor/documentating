# Final writer decision memo — current slice

Branch: `wave/current-slice-antora-cleanup-20260401`

This memo narrows the decision around the single final publication owner for the current repository slice.

## Decision question

Which workflow should eventually become the single canonical gh-pages / final publication writer for `smartresponsor/documentating`?

## Current candidates

### Candidate A — `.github/workflows/gh-pages.yml`

Strengths:
- canonical-looking name;
- still part of the top-level repo narrative;
- most natural long-term public entry for repository operators.

Weaknesses:
- currently tied to `tools/build_antora_site_v4.py`, which is classified as transitional live legacy;
- not yet aligned with intended base builder canon.

Assessment:
- best candidate for long-term canonical writer identity,
- but not yet clean in implementation.

### Candidate B — `.github/workflows/antora-gh-pages-owner.yml`

Strengths:
- appears to be a currently live legacy publication layer;
- may still reflect reality of what has been driving owner-facing publication.

Weaknesses:
- explicitly legacy in the current cleanup understanding;
- poor long-term canonical surface because of naming and transitional role.

Assessment:
- should not become the final canon;
- should remain only as a transitional live layer until superseded.

### Candidate C — `.github/workflows/publish-v19-pre-rc-quality-atlas-inline-after-v17.yml`

Strengths:
- cleanup canon indicates this is the intended current final publication layer;
- likely contains the most advanced atlas-aware pre-RC publication logic.

Weaknesses:
- versioned/transitional naming is too migration-specific for long-term canon;
- not ideal as the permanent public/operator-facing writer identity.

Assessment:
- strongest logic candidate,
- weak permanent naming candidate.

## Recommended decision shape

The repository should likely converge to this split:

1. **Final canonical writer identity**: `.github/workflows/gh-pages.yml`
2. **Final canonical builder facade**: `tools/build_antora_site.py`
3. **Final canonical implementation target**: logic converged from `tools/build_antora_site_v13.py` and atlas-aware layers proven through v17/v19 transition work
4. **Transitional live layers to preserve temporarily**:
   - `antora-gh-pages-owner.yml`
   - `publish-v17-quality-atlas-after-v16.yml`
   - `publish-v18-pre-rc-quality-atlas-after-v17.yml`
   - `publish-v19-pre-rc-quality-atlas-inline-after-v17.yml`
   - `tools/build_antora_site_v4.py`
   - `tools/build_antora_site_v17.py`

## Practical conclusion

The clean end-state should not be:
- keeping a versioned publish-v19 workflow forever,
- nor keeping owner-legacy workflow forever.

The clean end-state should be:
- `gh-pages.yml` as the single stable publication owner,
- `tools/build_antora_site.py` as the single stable builder entry,
- transitional logic folded inward until the versioned workflow layers are no longer needed.

## What must happen before deletion

Before deleting transitional publication layers, the repo needs explicit proof that:

1. `gh-pages.yml` owns the final publication path,
2. the selected builder path produces the required atlas/pre-RC outputs,
3. owner-facing publication behavior is preserved where still required,
4. no hidden workflow dependency still calls legacy builders.

## Immediate no-regret stance

Treat `gh-pages.yml` as the future canonical owner,
while treating `publish-v19-pre-rc-quality-atlas-inline-after-v17.yml` as the strongest current logic source,
and `antora-gh-pages-owner.yml` as live transitional legacy until superseded.
