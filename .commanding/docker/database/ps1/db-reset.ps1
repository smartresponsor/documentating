# Copyright (c) 2025 Oleksandr Tishchenko / Marketing America Corp

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$compose = Join-Path $PSScriptRoot '..\..\deploy\docker\compose-db.yml'
# WARNING: removes volumes (all local data).
docker compose -f $compose down -v --remove-orphans
