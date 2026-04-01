# Removal candidate ledger — current slice

Branch: `wave/current-slice-antora-cleanup-20260401`

This ledger lists concrete removal candidates and the proof condition required before each candidate may become deletion-ready.

## Workflow candidates

### `.github/workflows/antora-gh-pages-v2.yml`
Current status:
- removal-candidate after proof

Deletion-ready when:
- final writer ownership is proven;
- no active publication path depends on v2 logic;
- no unique durable logic remains only here.

### `.github/workflows/antora-gh-pages-v4.yml`
Current status:
- removal-candidate after proof

Deletion-ready when:
- final writer no longer needs any v4-era logic not already absorbed;
- builder path no longer depends on `build_antora_site_v4.py` by workflow design.

### `.github/workflows/antora-gh-pages-v5.yml`
Current status:
- removal-candidate after proof

Deletion-ready when:
- v5-specific publication behavior has either been absorbed or is obsolete.

### `.github/workflows/normalize-antora-repo-on-push.yml`
Current status:
- removal-candidate after proof

Deletion-ready when:
- repository normalization behavior is either no longer required or is folded into canonical build/publication flow.

### `.github/workflows/stabilize-antora-on-push.yml`
Current status:
- removal-candidate after proof

Deletion-ready when:
- stabilization logic is obsolete or preserved elsewhere;
- no live automation still depends on this transition helper.

### `.github/workflows/enable-owner-ui-on-push.yml`
Current status:
- removal-candidate after proof

Deletion-ready when:
- owner-facing UI behavior is fully resolved in canonical publication path or intentionally retired.

### `.github/workflows/switch-owner-v2-on-push.yml`
Current status:
- removal-candidate after proof

Deletion-ready when:
- owner playbook switching is no longer a live operational need.

## Versioned publish-layer candidates

### `.github/workflows/publish-v17-quality-atlas-after-v16.yml`
Current status:
- transitional, not deletion-ready yet

Deletion-ready when:
- atlas-aware logic is proven to live durably elsewhere;
- no required publication step still depends on the v17 layer.

### `.github/workflows/publish-v18-pre-rc-quality-atlas-after-v17.yml`
Current status:
- transitional, not deletion-ready yet

Deletion-ready when:
- pre-RC atlas behavior is reproduced by the final canonical path.

### `.github/workflows/publish-v19-pre-rc-quality-atlas-inline-after-v17.yml`
Current status:
- target-canon logic source, not deletion-ready

Deletion-ready when:
- its durable logic has been folded into the canonical final writer and builder path;
- it is no longer the strongest remaining source of final publish logic.

## Builder candidates

### `tools/build_antora_site_v2.py`
Current status:
- likely removal-candidate after proof

Deletion-ready when:
- no mapped active/transitional workflow still calls it;
- no reproducibility need keeps it relevant.

### `tools/build_antora_site_v4.py`
Current status:
- transitional live legacy, not deletion-ready

Deletion-ready when:
- final writer and builder path proof confirms live publication no longer depends on it.

### `tools/build_antora_site_v17.py`
Current status:
- transitional atlas-aware, not deletion-ready

Deletion-ready when:
- atlas/pre-RC logic is folded into the final canonical build path.

## Content/build residue candidates

### `.site/mkdocs.yml`
Current status:
- near-safe cleanup candidate

Deletion-ready when:
- no current process depends on MkDocs contour;
- Antora-only path remains the active canon.

### `ANTORA_TRANSITION.md`
Current status:
- likely cleanup candidate

Deletion-ready when:
- transition guidance is obsolete or preserved in current worklog/canon docs.

### Trigger residue under `.github/` and `docs/`
Current status:
- removal-candidate after proof

Deletion-ready when:
- no staged publication flow still uses trigger-file semantics.

## Operational note

This ledger does not grant deletion by itself.
It only records the proof condition required for each candidate to move into deletion-ready state.
