Contract checks validate *repository invariants*.

Scope:
- Root contract: only dot-folders in repo root + required files.
- .gitignore must match the consumer template requirements.

This folder must NOT contain linting checks (naming/style). Those belong to `.gate/linting/`.
