# Copyright (c) 2025 Oleksandr Tishchenko / Marketing America Corp

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$compose = Join-Path $PSScriptRoot '..\..\deploy\docker\compose-db.yml'
docker compose -f $compose up -d --remove-orphans
