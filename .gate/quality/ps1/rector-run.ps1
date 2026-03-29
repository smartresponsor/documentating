param(
  [Parameter(Mandatory=$false)][string]$RepoRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"
$cfg = Join-Path $RepoRoot ".gate/quality/php/rector.php"
if (-not (Test-Path $cfg)) { throw "rector.php not found: $cfg" }

$bin = Join-Path $RepoRoot "vendor/bin/rector"
if (-not (Test-Path $bin)) { throw "rector binary not found. Run composer install." }

& $bin process --config $cfg
