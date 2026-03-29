# Copyright (c) 2025 Oleksandr Tishchenko / Marketing America Corp
<#
Intelligence Install (minimal)
- Installs Intelligence workflows into .github/workflows/
- Mirrors Intelligence files into .Intelligence/
#>

param(
  [Parameter(Mandatory=$false)][string]$Repo = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Resolve-RepoRoot {
  param([string]$RepoArg)
  if ($RepoArg -and (Test-Path -LiteralPath $RepoArg)) { return (Resolve-Path -LiteralPath $RepoArg).Path }
  return (Get-Location).Path
}

$repoRoot = Resolve-RepoRoot -RepoArg $Repo
$srcRoot  = $PSScriptRoot
$wfSrc    = Join-Path $srcRoot "workflow"

$wfDst    = Join-Path $repoRoot ".github\workflows"
$intDst   = Join-Path $repoRoot ".Intelligence"

New-Item -ItemType Directory -Force -Path $wfDst | Out-Null
New-Item -ItemType Directory -Force -Path $intDst | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $intDst "workflow") | Out-Null

# 1) Workflows
Get-ChildItem -LiteralPath $wfSrc -Filter "*.yml" | ForEach-Object {
  Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $wfDst $_.Name) -Force
}

# 2) Mirror entrypoints + config
$entry = @(
  "intelligence-install.ps1",
  "intelligence-engine.ps1",
  "intelligence-run.ps1",
  "intelligence.json"
)

foreach ($f in $entry) {
  $p = Join-Path $srcRoot $f
  if (Test-Path -LiteralPath $p) {
    Copy-Item -LiteralPath $p -Destination (Join-Path $intDst $f) -Force
  }
}

# 3) Mirror workflows (for visibility inside repo)
Get-ChildItem -LiteralPath $wfSrc -Filter "*.yml" | ForEach-Object {
  Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $intDst "workflow\$($_.Name)") -Force
}

# 4) Ensure config exists
$cfgPath = Join-Path $intDst "intelligence.json"
if (-not (Test-Path -LiteralPath $cfgPath)) {
  $domain = (Split-Path -Leaf $repoRoot)
  $cfg = @{ domain = $domain; profile = "chatgpt-codex"; version = "v1" } | ConvertTo-Json -Depth 5
  Set-Content -LiteralPath $cfgPath -Value $cfg -Encoding UTF8
}

Write-Host "INT_INSTALL: OK"
Write-Host "INT_INSTALL: workflows -> $wfDst"
Write-Host "INT_INSTALL: mirror -> $intDst"
