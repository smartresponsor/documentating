# deploy/cloudflare

Intent
- Cloudflare deployment method (Workers / Pages) using Wrangler.
- This is used for edge logic, docs, portals, or light BFF endpoints.

What belongs here
- wrangler.toml templates
- worker source (if this repo owns it) or deployment glue
- routes, environments, KV/D1/R2 bindings templates
- notes for build & publish

Suggested tree
- wrangler.toml
- worker/
  - src/
- doc/
  - publish.md
