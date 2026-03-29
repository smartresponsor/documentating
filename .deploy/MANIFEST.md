# SmartResponsor deploy/ skeleton

Purpose
- This package provides the canonical `deploy/` folder layout for SmartResponsor repositories.
- `deploy/` contains *deployment methods* (how to run / ship), not domain logic and not runtime application code.

Rules
- Keep repository root clean for runtime projects (Symfony-friendly).
- Put each deployment method into its own subfolder under `deploy/`.
- No runtime data, no secrets, no large binaries in this tree.

Folders
- deploy/docker      : Docker Compose based local/dev deployment (and lightweight staging).
- deploy/helm        : Kubernetes/Helm deployment method (cluster environments).
- deploy/systemd     : Bare-metal / VM deployment method using systemd units.
- deploy/cloudflare  : Cloudflare deployment method (Workers/Pages/Wrangler).
- deploy/_template   : Notes and copy-ready stubs for future deployment methods.

Created
- 2026-01-23 (America/Chicago)
