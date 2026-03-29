# deploy/docker

Intent
- Docker Compose based environment for local development and simple staging.
- This folder is about *running* the stack via containers.

What belongs here
- compose.yaml / docker-compose.yml
- service configs for containerized dependencies (kafka/redis/postgres/observability)
- helper scripts (up/down/reset), all portable (PowerShell + Bash if possible)
- .env.example (NO secrets)

What must NOT be here
- runtime application source code (keep it in the service repo root: src/, config/, etc.)
- secrets (never commit real credentials)
- large data volumes (use named volumes or ./var with gitignored paths)

Suggested tree
- compose.yaml
- service/
  - kafka/
  - redis/
  - prometheus/
  - grafana/
- tool/
  - up.ps1 / up.sh
  - down.ps1 / down.sh
  - reset.ps1 / reset.sh
