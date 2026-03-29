\
param(
  [Parameter(Mandatory = $false)]
  [string]$RepoRoot = "."
)

$policyPath = $env:GATE_GITIGNORE_POLICY
if ([string]::IsNullOrWhiteSpace($policyPath)) {
  $policyPath = Join-Path $RepoRoot ".gate/policy/acceptable/gitignore-template.yml"
}

if (!(Test-Path -LiteralPath $policyPath)) {
  Write-Host ".gitignore template FAILED:`n"
  Write-Host " - missing policy: $policyPath"
  exit 3
}

# policy is JSON (valid YAML)
$policyJson = Get-Content -LiteralPath $policyPath -Raw -Encoding UTF8
$policy = $policyJson | ConvertFrom-Json

$gitignorePath = Join-Path $RepoRoot ".gitignore"
if (!(Test-Path -LiteralPath $gitignorePath)) {
  Write-Host ".gitignore template FAILED:`n"
  Write-Host " - missing: .gitignore`n"
  exit 3
}

$lines = Get-Content -LiteralPath $gitignorePath -Encoding UTF8
$missing = New-Object System.Collections.Generic.List[string]

foreach ($req in $policy.template.required) {
  $found = $false
  foreach ($l in $lines) {
    if ($l -ceq $req) { $found = $true; break }
  }
  if (-not $found) { $missing.Add($req) }
}

if ($missing.Count -gt 0) {
  Write-Host ".gitignore template FAILED:`n"
  foreach ($m in $missing) {
    Write-Host " - missing: $m`n"
  }
  exit 3
}

Write-Host ".gitignore template OK"
exit 0
