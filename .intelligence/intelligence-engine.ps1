# Copyright (c) 2025 Oleksandr Tishchenko / Marketing America Corp
<#
Intelligence Engine (minimal)
Entrypoint for running domain automation (plan/codex) in CI or locally.
#>

param(
  [Parameter(Mandatory=$false)][ValidateSet('plan','codex','pr')][string]$Task = 'pr',
  [Parameter(Mandatory=$false)][string]$Domain = '',
  [Parameter(Mandatory=$false)][string]$Repo = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Resolve-RepoRoot {
  param([string]$RepoArg)
  if ($RepoArg -and (Test-Path -LiteralPath $RepoArg)) { return (Resolve-Path -LiteralPath $RepoArg).Path }
  return (Get-Location).Path
}

function Resolve-Domain {
  param([string]$RepoRoot, [string]$DomainArg)
  if ($DomainArg -and $DomainArg.Trim().Length -gt 0) { return $DomainArg.Trim() }

  $cfgPath = Join-Path $RepoRoot ".Intelligence\intelligence.json"
  if (Test-Path -LiteralPath $cfgPath) {
    try {
      $cfg = Get-Content -LiteralPath $cfgPath -Raw | ConvertFrom-Json
      if ($cfg.domain -and $cfg.domain.Trim().Length -gt 0) { return $cfg.domain.Trim() }
    } catch {}
  }

  return (Split-Path -Leaf $RepoRoot)
}

function Invoke-DomainTool {
  param([string]$RepoRoot, [string]$DomainName, [string]$Cmd)

  $toolPath = Join-Path $RepoRoot "Domain\Tool\run.ps1"
  if (-not (Test-Path -LiteralPath $toolPath)) {
    throw "Domain tool not found: $toolPath"
  }

  Write-Host "INT_ENGINE: $Cmd (domain=$DomainName)"
  pwsh -NoProfile -File $toolPath $Cmd -Domain $DomainName -Repo $RepoRoot
}

$repoRoot = Resolve-RepoRoot -RepoArg $Repo
$domainName = Resolve-Domain -RepoRoot $repoRoot -DomainArg $Domain

$env:INT_DOMAIN = $domainName
$env:INT_TASK = $Task

# Minimal and forgiving: health/validate are optional in early stage.
try { Invoke-DomainTool -RepoRoot $repoRoot -DomainName $domainName -Cmd "health" } catch { Write-Host "INT_ENGINE: health skipped ($($_.Exception.Message))" }
try { Invoke-DomainTool -RepoRoot $repoRoot -DomainName $domainName -Cmd "validate" } catch { Write-Host "INT_ENGINE: validate skipped ($($_.Exception.Message))" }

if ($Task -eq 'plan') {
  try { Invoke-DomainTool -RepoRoot $repoRoot -DomainName $domainName -Cmd "plan" } catch { Write-Host "INT_ENGINE: plan skipped ($($_.Exception.Message))" }
  exit 0
}

if ($Task -eq 'codex' -or $Task -eq 'pr') {
  try { Invoke-DomainTool -RepoRoot $repoRoot -DomainName $domainName -Cmd "plan" } catch { Write-Host "INT_ENGINE: plan skipped ($($_.Exception.Message))" }
  try { Invoke-DomainTool -RepoRoot $repoRoot -DomainName $domainName -Cmd "codex" } catch { Write-Host "INT_ENGINE: codex failed ($($_.Exception.Message))" ; throw }
  exit 0
}

throw "Unsupported task: $Task"
