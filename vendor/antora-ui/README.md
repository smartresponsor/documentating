# Vendored Antora UI bundle

This directory stores the local Antora UI bundle used by the publication contract.

Contract:

- canonical local bundle path: `vendor/antora-ui/ui-bundle.zip`
- checksum file: `vendor/antora-ui/ui-bundle.zip.sha256`
- bootstrap / refresh script: `tools/ensure_local_ui_bundle.sh`
- manual refresh workflow: `.github/workflows/refresh-local-ui-bundle.yml`

Why this exists:

- normal site builds should not depend on a floating remote UI snapshot URL
- the repository should own the exact UI artifact used for publication
- UI updates should happen only by explicit refresh intent

Do not edit the bundle archive by hand.
Refresh it through the dedicated workflow or script.
