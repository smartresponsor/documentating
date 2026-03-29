\
param(
  [Parameter(Mandatory=$false)]
  [string]$RepoRoot = ".",
  [Parameter(Mandatory=$false)]
  [ValidateSet("", "print", "safe", "print-safe")]
  [string]$Mode = ""
)

$gate = Join-Path $PSScriptRoot ".gate/gate.ps1"
if (!(Test-Path -LiteralPath $gate)) {
  Write-Host "[run] missing .\.gate\gate.ps1"
  exit 2
}

# Run gate (prefer passing -Path if supported)
$rc = 0
try {
  & $gate -Path $RepoRoot
  $rc = $LASTEXITCODE
} catch {
  # fallback for older gate.ps1 without -Path
  & $gate $RepoRoot
  $rc = $LASTEXITCODE
}

$proposal = Join-Path $PSScriptRoot ".report/gate-fix-proposal.ndjson"
$fix = Join-Path $PSScriptRoot ".gate/contract/ps1/fail-fixer-run.ps1"

if ($Mode -eq "print" -or $Mode -eq "print-safe" -or $Mode -eq "safe") {
  if (Test-Path -LiteralPath $proposal) {
    if (Test-Path -LiteralPath $fix) {
      if ($Mode -eq "print" -or $Mode -eq "print-safe") {
        pwsh -File $fix -RepoRoot $RepoRoot -PrintOnly | Out-Host
      }
      if ($Mode -eq "safe" -or $Mode -eq "print-safe") {
        # ApplySafe is optional; if your fixer script supports it, it will apply
        pwsh -File $fix -RepoRoot $RepoRoot | Out-Host
      }
    } else {
      Write-Host "[run] missing fixer: $fix"
    }
  }
}

exit $rc
