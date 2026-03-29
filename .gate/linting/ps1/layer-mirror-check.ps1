# Copyright (c) 2025 Oleksandr Tishchenko / Marketing America Corp
param(
  [string]$Path = ".",
  [string]$Report = "report/layer-mirror-check.json",
  [switch]$NoWrite
)
$ErrorActionPreference = "Stop"
$root = Resolve-Path -Path $Path
$arg = @("--path", $root, "--report", $Report)
if ($NoWrite) { $arg += "--no-write" }
node (Join-Path $PSScriptRoot "layer-mirror-check.js") @arg
exit $LASTEXITCODE
