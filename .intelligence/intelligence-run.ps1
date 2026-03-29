# Copyright (c) 2025 Oleksandr Tishchenko / Marketing America Corp
<#
Intelligence Run (minimal)
Local runner for Intelligence Engine.
#>

param(
  [Parameter(Mandatory=$false)][ValidateSet('plan','codex','pr')][string]$Task = 'codex',
  [Parameter(Mandatory=$false)][string]$Domain = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = (Get-Location).Path
$engine = Join-Path $PSScriptRoot "intelligence-engine.ps1"

pwsh -NoProfile -File $engine -Task $Task -Domain $Domain -Repo $repoRoot
