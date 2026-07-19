# Vendored UI switch

This note documents the minimal canonical switch from the floating remote Antora reference UI bundle to the repository-owned local vendored bundle contract.

## What already exists on this branch

- local bundle bootstrap script: `tools/ensure_local_ui_bundle.sh`
- local bundle contract directory: `vendor/antora-ui/`
- manual refresh workflow: `.github/workflows/refresh-local-ui-bundle.yml`
- switch-ready local playbook: `antora-playbook-local-ui.yml`
- proof workflow: `.github/workflows/prove-local-vendored-ui.yml`

## Minimal canonical switch

1. Replace the current `ui.bundle.url` in `antora-playbook.yml` with:

```yml
ui:
  bundle:
    url: ./vendor/antora-ui/ui-bundle.zip
  supplemental_files: ./supplemental-ui
```

2. Remove `snapshot: true` from the canonical playbook.

3. In `.github/workflows/gh-pages.yml`, before the Antora build step, add:

```bash
bash tools/ensure_local_ui_bundle.sh
```

4. Build the site using the canonical playbook after the vendored bundle is present.

## Result

After that switch:

- normal docs builds use a repository-owned local UI artifact
- UI drift from the floating remote bundle is removed from the normal publication path
- UI updates happen only through explicit refresh intent
