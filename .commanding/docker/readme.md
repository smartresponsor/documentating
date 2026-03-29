# deploy/docker

This folder is the canonical Docker entrypoint for local development and IDE Data Source.

## Start databases (PostgreSQL + MySQL)

PowerShell:

- `tools/deploy/db-up.ps1`
- `tools/deploy/db-down.ps1`
- `tools/deploy/db-reset.ps1`

Or manual:

- `docker compose -f deploy/docker/compose-db.yml up -d`

PostgreSQL: `127.0.0.1:5432` (db/user/pass: `app/app/app`)

MySQL: `127.0.0.1:3306` (db/user/pass: `app/app/app`, root pass: `root`)

## PhpStorm / JetBrains Data Source

Create two Data Sources:

- PostgreSQL: host `127.0.0.1`, port `5432`, database `app`, user `app`, password `app`
- MySQL: host `127.0.0.1`, port `3306`, database `app`, user `app`, password `app`

Then:

1. Introspect / Synchronize.
2. In PostgreSQL Data Source, enable schema `taxation` (Schemas tab) if you use `taxation.*` tables.
3. Attach Data Source for SQL inspection where needed (Alt+Enter on the warning).

### Mixed dialect SQL in one PHP file

If a file contains both PostgreSQL and MySQL SQL strings, mark each SQL string explicitly:

- `/** @lang PostgreSQL */`
- `/** @lang MySQL */`

This prevents "CONFLICT expected, got 'DUPLICATE'"-style parser mismatches.

## App stack (optional)

If the repo has a `Dockerfile`, you can run:

- `docker compose -f deploy/docker/compose-app.yml up -d --build`
