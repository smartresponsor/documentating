#!/usr/bin/env sh
# Copyright (c) 2025 Oleksandr Tishchenko / Marketing America Corp
set -eu

docker compose -f deploy/docker/compose-db.yml up -d --remove-orphans
