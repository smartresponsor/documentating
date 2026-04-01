# Cleanup execution order — current slice

Branch: `wave/current-slice-antora-cleanup-20260401`

This document defines a practical execution order for collapsing builder/workflow layers in the current repository slice without breaking publication behavior.

## Objective

Move the repository from multi-layer transitional publication logic to a cleaner Antora-first canon with:

- one stable publication owner,
- one stable builder entry,
- preserved atlas/pre-RC behavior,
- minimized legacy residue.

## Execution order

### Phase 1 — Freeze the decision frame

Goal:
- stop making cleanup decisions ad hoc.

Actions:
1. Treat `gh-pages.yml` as the intended future canonical publication owner.
2. Treat `tools/build_antora_site.py` as the intended stable builder facade.
3. Treat `publish-v19-pre-rc-quality-atlas-inline-after-v17.yml` as the strongest current logic source.
4. Treat `antora-gh-pages-owner.yml` and `tools/build_antora_site_v4.py` as transitional live legacy, not immediate delete targets.

Exit condition:
- builder/workflow truth layers are explicitly named before any structural deletion wave begins.

### Phase 2 — Make builder ownership explicit

Goal:
- ensure the final public/operator builder entry is unambiguous.

Actions:
1. Preserve `tools/build_antora_site.py` as the stable entry point.
2. Decide whether its underlying implementation should converge directly to `tools/build_antora_site_v13.py` or to a merged atlas-aware successor.
3. Preserve `tools/build_antora_site_v4.py` until all active publication layers stop depending on it.
4. Preserve `tools/build_antora_site_v17.py` until atlas/pre-RC behavior is folded into the final canon path.

Exit condition:
- one builder facade, one target implementation direction, legacy builders still available only as transitional dependencies.

### Phase 3 — Prove final writer ownership

Goal:
- make one workflow the actual final publication owner.

Actions:
1. Align `gh-pages.yml` with the chosen builder canon target.
2. Ensure the final publication writer reproduces required atlas/pre-RC outputs.
3. Verify no hidden owner-legacy workflow still owns production publication.
4. Verify no hidden dependency still calls `build_antora_site_v4.py` where it should not.

Exit condition:
- `gh-pages.yml` is not only nominally canonical, but functionally the final writer.

### Phase 4 — Collapse versioned publication layers

Goal:
- reduce publish workflow proliferation.

Actions:
1. Reclassify `publish-v17-*`, `publish-v18-*`, and `publish-v19-*` after final writer proof.
2. Fold durable logic into the canonical writer/builder path.
3. Move remaining versioned publication files to removal-candidate status if they no longer own behavior.

Exit condition:
- no versioned publish workflow remains necessary for normal operation.

### Phase 5 — Remove migration automation residue

Goal:
- eliminate transition-only automations once no longer needed.

Actions:
1. Review `normalize-antora-repo-on-push.yml`.
2. Review `stabilize-antora-on-push.yml`.
3. Review `enable-owner-ui-on-push.yml`.
4. Review `switch-owner-v2-on-push.yml`.
5. Remove them only after confirming their logic has either been absorbed or is obsolete.

Exit condition:
- migration helpers no longer define live behavior.

### Phase 6 — Evacuate obvious content/build residue

Goal:
- clean out stale narrative and obsolete build contours.

Actions:
1. Rewrite `README.md` to Antora-first truth.
2. Remove `.site/mkdocs.yml`.
3. Remove obsolete trigger files after verifying they are not still used by any staged flow.
4. Keep preservation-first classification for early useful source materials.

Exit condition:
- repo narrative and build contours no longer contradict actual canon.

### Phase 7 — Finish UI runtime cleanup

Goal:
- repair surface issues only after the truth layers are stabilized.

Actions:
1. Patch `supplemental-ui/css/owner-overrides.css` so it no longer hides `.nav-panel-explore`.
2. Re-check mobile sidebar behavior.
3. Audit other header/nav overrides only after the primary blocker is removed.

Exit condition:
- mobile/sidebar navigation works without relying on accidental transitional behavior.

## No-regret sequencing summary

Do this in order:

1. decide canon,
2. align builder,
3. prove final writer,
4. collapse versioned publish layers,
5. remove migration helpers,
6. remove obvious stale MkDocs/build residue,
7. finish narrow UI cleanup.

## Main warning

Do **not** start by deleting old workflows just because they look redundant.
In the current slice, several of them still represent live or semi-live behavior layers.
