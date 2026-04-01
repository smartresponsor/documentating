# First-wave Antora cleanup patch plan

Branch: `wave/antora-cleanup-mobile-nav`

This file records the exact first-wave changes that should be applied to existing files.
It exists because the current GitHub connector session can create new files, but updating existing tracked files is blocked by the wrapper not exposing the `sha` parameter required by GitHub Contents API updates.

## 1. README.md

Replace current README narrative with:

```md
# documentating

Public documentation portal for Smart Responsor.

- Canonical site engine: Antora
- Canonical playbook: `antora-playbook.yml`
- Canonical source build helper: `tools/build_antora_site_v4.py`
- Generated Antora source tree: `.antora-src/`
- Supplemental Antora UI overrides: `supplemental-ui/`
- GitHub Pages deployment: `.github/workflows/gh-pages.yml`
- Content source: `docs/`
- Component registry: `.sync/manifest/component-list.yml`
```

Rationale:
- remove false MkDocs/Material narrative
- align repo description with actual Antora-first build path

## 2. `.site/mkdocs.yml`

Delete file.

Rationale:
- legacy MkDocs/Material build contour
- no longer canonical after Antora migration
- safe delete candidate as build legacy, not as a valuable content source

## 3. `supplemental-ui/css/owner-overrides.css`

Current problematic block:

```css
.nav-menu > .title,
.nav-panel-explore,
.edit-this-page {
  display: none !important;
}
```

Replace with:

```css
.nav-menu > .title,
.edit-this-page {
  display: none !important;
}
```

Leave the rest unchanged for the first wave.

Rationale:
- stop globally hiding `.nav-panel-explore`
- this is the prime suspect for the broken mobile/sidebar navigation
- keep the fix narrow and low-risk

## 4. Post-wave verification focus

After the above changes land, verify:
- mobile sidebar can open
- desktop navigation still renders acceptably
- no additional navbar control is hidden incorrectly
- no remaining MkDocs/Material narrative remains in top-level docs

## Evidence snapshot

Confirmed earlier in this wave:
- `README.md` still describes MkDocs Material
- `.site/mkdocs.yml` still exists
- `owner-overrides.css` hides `.nav-panel-explore`
