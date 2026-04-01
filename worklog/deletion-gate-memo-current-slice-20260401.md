# Deletion gate memo — current slice

Branch: `wave/current-slice-antora-cleanup-20260401`

This memo defines deletion gates for the current cleanup wave.
Its purpose is to prevent accidental removal of live, semi-live, or still-unproven publication logic.

## Gate categories

### Category A — Do not delete now

These files/layers must be preserved in the current wave because they still represent live, semi-live, or not-yet-proven behavior.

- `.github/workflows/gh-pages.yml`
- `.github/workflows/antora-gh-pages-owner.yml`
- `.github/workflows/publish-v17-quality-atlas-after-v16.yml`
- `.github/workflows/publish-v18-pre-rc-quality-atlas-after-v17.yml`
- `.github/workflows/publish-v19-pre-rc-quality-atlas-inline-after-v17.yml`
- `tools/build_antora_site.py`
- `tools/build_antora_site_v4.py`
- `tools/build_antora_site_v13.py`
- `tools/build_antora_site_v17.py`

Reason:
- these files still participate in either live publication, intended canon, or transitional atlas-aware logic.

### Category B — Delete only after proof

These files are strong removal-candidates, but deletion requires proof that their logic has either been absorbed or is no longer used.

- `.github/workflows/antora-gh-pages-v2.yml`
- `.github/workflows/antora-gh-pages-v4.yml`
- `.github/workflows/antora-gh-pages-v5.yml`
- `.github/workflows/normalize-antora-repo-on-push.yml`
- `.github/workflows/stabilize-antora-on-push.yml`
- `.github/workflows/enable-owner-ui-on-push.yml`
- `.github/workflows/switch-owner-v2-on-push.yml`
- old publish trigger files under `.github/` and `docs/` that were created only to force publication waves
- older numbered builder generations not mapped to active or transitional workflows

Required proof examples:
- `gh-pages.yml` is the actual final writer;
- no active workflow still calls the file;
- target logic is already preserved elsewhere;
- atlas/pre-RC output path remains reproducible without the candidate.

### Category C — Safe early cleanup candidates

These items are safe or near-safe cleanup candidates because they represent obvious narrative/build residue rather than uncertain live behavior.

- `README.md` stale MkDocs/Material wording (rewrite, not full delete)
- `.site/mkdocs.yml`
- stale transition notes such as `ANTORA_TRANSITION.md` once no longer needed for human guidance
- clearly obsolete trigger residue that has no current workflow dependency

Reason:
- these do not appear to be the primary owners of live publication behavior.

## Deletion gate rules

1. No workflow deletion before final writer ownership is proven.
2. No builder deletion before workflow-to-builder mapping is explicit.
3. No atlas-related layer deletion before output parity is proven.
4. No early source deletion before classification says it is build legacy, duplicate, or noise.
5. UI/runtime files are patch candidates first, deletion candidates last.

## Immediate working stance

In the current wave:
- preserve all live/transitional truth layers;
- delete only obvious build residue or stale narrative after minimal verification;
- defer structural deletions until the final writer and builder canon are explicit.

## Practical consequence

The current cleanup wave is a **decision-hardening wave**, not yet a mass-deletion wave.
