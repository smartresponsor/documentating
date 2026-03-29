param(
  [Parameter(Mandatory=$false)][string]$RepoRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"
$cfg = Join-Path $RepoRoot ".gate/quality/php/phpstan.neon"
if (-not (Test-Path $cfg)) { throw "phpstan.neon not found: $cfg" }

# expects vendor/bin/phpstan
$bin = Join-Path $RepoRoot "vendor/bin/phpstan"
if (-not (Test-Path $bin)) { throw "phpstan binary not found. Run composer install." }

& $bin analyse -c $cfg
