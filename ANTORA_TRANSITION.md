# Antora transition status

The repository now uses one normal publication contract and one normal builder line.

## Canonical normal path

- build entry: `tools/build_antora_site.py`
- publish owner: `.github/workflows/gh-pages.yml`
- playbook: `antora-playbook.yml`
- asset source: `assets/`

## Removed legacy surface

This wave intentionally removed the legacy surface instead of carrying transitional replay shells forward:

- versioned and owner-oriented workflows under `.github/workflows/`
- owner playbooks `antora-playbook-owner*.yml`
- removed legacy wrapper builders `tools/build_antora_site_v2.py`, `v5.py`, `v6.py`, `v7.py`, `v9.py`, `v13.py`, `v14.py`, `v15.py`, `v17.py`

## Canonical builder line

The remaining transitional builder composition has been fully evacuated.

- `tools/build_antora_site_v4.py` has now been evacuated into `tools/build_antora_site.py`.
- the canonical builder line is now a single file: `tools/build_antora_site.py`

There is no remaining active multi-file builder composition in the normal path.

## Atlas generator contract

The canonical normal-path atlas generator is now only:

- `tools/generate_pre_rc_quality_atlas.py`

The older general-purpose generator `tools/generate_quality_atlas.py` has been removed as legacy residue.

## Generated index contract

The canonical portal index surfaces are now generated only by `tools/build_antora_site.py`.

Removed legacy markdown index residues:

- `docs/index.md`
- `docs/article/index.md`
- `docs/component/index.md`

These files were already skipped by the canonical builder and no longer remain in the repository.


## Skipped-source residue evacuation

The canonical builder no longer carries repository residue that it only skipped by rule.

Removed skipped-source residues:

- `docs/article/2026-03-29--tesr.md`
- `docs/article/2026-03-29--2026-03-29-technological-inequality-2-0-cognitive-divide.md`
- `docs/article/odyssey-who-is-announcement.md`
- `docs/article/2026-03-29--why-the-next-e-commerce-will-not-be-a-store-with-ai.md`
- `docs/articles/2026-03-29-the-first-great-war-between-platforms-and-protocols.md`

The legacy `docs/articles/` surface has also been removed.

The canonical article source surface is now only:

- `docs/article/`

## UI identity and script parity

- `supplemental-ui/partials/footer.hbs` now uses the canonical identity line:
  - `Marketing America Corp · High Hopes · Oleksandr Tishchenko`
- duplicate `site.js` loading was removed from `supplemental-ui/partials/footer-scripts.hbs`
- canonical script loading now lives only in `supplemental-ui/partials/header-scripts.hbs` with `defer`
