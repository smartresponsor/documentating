# Final writer proof checklist — current slice

Branch: `wave/current-slice-antora-cleanup-20260401`

This checklist defines what must be proven before transitional publication layers can be collapsed and before the repository can honestly claim a single final publication owner.

## Proof objective

Prove that one workflow is not only nominally preferred, but functionally owns the final publication path for `smartresponsor/documentating`.

## Candidate target

Current intended target:
- final canonical writer identity: `.github/workflows/gh-pages.yml`
- final stable builder entry: `tools/build_antora_site.py`

## Required proof items

### 1. Publication ownership proof

Must be true:
- `gh-pages.yml` is the workflow that actually owns the final publication path;
- no transitional legacy workflow remains the effective writer by hidden convention or operator habit.

Evidence examples:
- workflow references and docs point to `gh-pages.yml` as the final owner;
- no parallel writer continues to push competing output for normal operation.

### 2. Builder path proof

Must be true:
- the final writer uses the intended stable builder entry or an explicitly approved target canonical builder path;
- no hidden dependency keeps the live publication path on `tools/build_antora_site_v4.py` by accident.

Evidence examples:
- workflow steps call the canonical builder path;
- staged legacy builder references are either removed or explicitly transitional.

### 3. Output parity proof

Must be true:
- required site outputs still exist after the final writer alignment;
- atlas/pre-RC publication behavior remains reproducible where required.

Evidence examples:
- generated site structure matches expected publish surface;
- atlas-linked outputs remain present and valid;
- no regression in public documentation entry points.

### 4. Owner-facing behavior proof

Must be true:
- anything still needed from owner-facing publication layers is preserved in the final path or intentionally retired;
- removing `antora-gh-pages-owner.yml` would not silently drop needed behavior.

Evidence examples:
- owner-specific UI/publication behavior is either migrated or intentionally deprecated with no hidden dependency.

### 5. Workflow exclusivity proof

Must be true:
- versioned publish workflows are no longer required for ordinary operation;
- final writer ownership is exclusive enough that transitional layers can move to removal-candidate status.

Evidence examples:
- `publish-v17*`, `publish-v18*`, and `publish-v19*` are no longer the only place where durable publication logic lives.

### 6. Cleanup safety proof

Must be true:
- removing transitional layers will not erase unique logic that has not been absorbed into the canonical path.

Evidence examples:
- mapping matrix remains valid after consolidation;
- deletion gate conditions are satisfied for each removal candidate.

## Exit condition

The repository may move from decision-hardening into structural collapse only when all of the following are true:

1. final writer identity is explicit,
2. builder path is explicit,
3. output parity is preserved,
4. owner-facing dependency is resolved,
5. versioned publish layers are no longer operationally necessary,
6. deletion safety is demonstrated.

## Practical use

This checklist should be used as the gate before:
- deleting transitional publish workflows,
- deleting transitional builders,
- claiming the repo has one clean publication canon.
