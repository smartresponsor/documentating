# Quality Atlas canonical switch plan

Branch: `feature/quality-atlas-candidate-files`

## Goal

Promote Quality Atlas from candidate files into the canonical live publication path.

## Candidate files in this branch

- `doc/quality-atlas/component-quality-dataset.json`
- `doc/quality-atlas/component-quality-summary.adoc`
- `doc/quality-atlas/home-quality-atlas-block.adoc`
- `doc/quality-atlas/integration-note.md`
- `tools/build_antora_site_quality_atlas_candidate.py`
- `tools/build_antora_site_canonical_with_quality_atlas.py`

## Canonical switch

### 1. Builder entry

Replace the live builder entry command in `gh-pages.yml`:

```bash
python3 tools/build_antora_site.py
```

with:

```bash
python3 tools/build_antora_site_canonical_with_quality_atlas.py
```

### 2. Validation targets

Confirm after a run that the following exist in `.antora-src`:

- `modules/ROOT/pages/quality-atlas/component-quality-summary.adoc`
- `modules/ROOT/nav.adoc` contains `Quality Atlas`
- `modules/ROOT/pages/index.adoc` contains `== Quality Atlas`

### 3. Canonical replacement

After validation, either:

- replace `tools/build_antora_site.py` with the contents of `tools/build_antora_site_canonical_with_quality_atlas.py`,

or:

- rename `tools/build_antora_site_canonical_with_quality_atlas.py` to `tools/build_antora_site.py`
  and update references accordingly.

### 4. Cleanup after successful switch

Remove candidate-only files that are no longer needed:

- `tools/build_antora_site_quality_atlas_candidate.py`
- `tools/build_antora_site_canonical_with_quality_atlas.py`
- `doc/quality-atlas/integration-note.md`

Keep as source-of-truth content:

- `doc/quality-atlas/component-quality-dataset.json`
- `doc/quality-atlas/component-quality-summary.adoc`
- `doc/quality-atlas/home-quality-atlas-block.adoc`

## Meaning contract

Quality Atlas is a **pre-RC / before v1** quality surface.
It is not a production SLA dashboard.
