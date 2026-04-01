# Implementation wave proposal — current slice

Branch: `wave/current-slice-antora-cleanup-20260401`

This proposal defines the first practical implementation wave that should follow the current decision-hardening wave.

## Objective

Execute a narrow but meaningful structural wave that moves the repository closer to one canonical publication line without triggering premature mass deletion.

## Scope principle

This wave should:
- change a small number of high-leverage files,
- preserve live/transitional layers,
- improve truth alignment,
- avoid irreversible collapse before proof gates are satisfied.

## Proposed first implementation wave

### Package A — Canonical narrative and obvious build residue

Target changes:
1. Rewrite `README.md` to Antora-first truth.
2. Remove `.site/mkdocs.yml`.
3. Review `ANTORA_TRANSITION.md` and either retain as temporary human guidance or mark it as cleanup-ready.

Why first:
- these are high-confidence residue corrections;
- they improve repo truth without collapsing live publication logic.

### Package B — Explicit builder/workflow annotation layer

Target changes:
1. Add short inline comments or companion documentation that make the intended roles of `gh-pages.yml`, `build_antora_site.py`, `build_antora_site_v4.py`, `build_antora_site_v13.py`, and `build_antora_site_v17.py` explicit.
2. Avoid deleting legacy files yet; make their transitional role obvious instead.

Why second:
- truth alignment should precede destructive cleanup;
- reduces future accidental deletions.

### Package C — Narrow UI blocker fix

Target changes:
1. Patch `supplemental-ui/css/owner-overrides.css` so it no longer hides `.nav-panel-explore`.
2. Do not widen UI cleanup beyond that in the first implementation wave.

Why third:
- it is likely the main mobile/sidebar blocker;
- it is a narrow, low-churn fix;
- it should not be mixed with larger workflow/builder restructuring.

## What this implementation wave should NOT do

Do not do the following yet:
- delete `antora-gh-pages-owner.yml`;
- delete `publish-v17/v18/v19` layers;
- delete `tools/build_antora_site_v4.py`;
- delete `tools/build_antora_site_v17.py`;
- claim builder/workflow collapse is complete;
- start broad article/source cleanup unrelated to the current structural proof track.

## Expected result after this wave

If Packages A/B/C land, the repository should be in a better state because:
- top-level repo truth aligns with Antora reality;
- obvious MkDocs residue is reduced;
- the mobile/sidebar blocker is at least partially addressed;
- transitional layers remain preserved, but with clearer meaning.

## Next wave after that

Only after the above lands should the repo move toward:
1. proving final writer ownership in practice,
2. aligning the canonical writer with canonical builder path,
3. collapsing versioned publication layers,
4. removing migration automation residue.

## Practical note

This is a deliberately conservative implementation wave.
Its purpose is to convert the current analysis/governance scaffold into the first safe structural movement, not to finish the entire cleanup in one jump.
