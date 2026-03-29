#!/usr/bin/env sh
# Copyright (c) 2025 Oleksandr Tishchenko / Marketing America Corp
set -eu

# WARNING: removes volumes (all local data).
docker compose -f deploy/docker/compose-db.yml down -v --remove-orphans
