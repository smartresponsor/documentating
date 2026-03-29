\
param(
  [Parameter(Mandatory=$false)]
  [Alias('Path')]
  [string]$RepoRoot = "."
)

$resolved = (Resolve-Path -Path $RepoRoot).Path

if (-not (Get-Command bash -ErrorAction SilentlyContinue)) {
  throw "bash not found. Install Git for Windows (Git Bash) or provide bash in PATH."
}

# gate.sh auto-detects CI (GITHUB_ACTIONS/CI). RepoRoot is passed as an argument.
bash "$resolved/.gate/gate.sh" "$resolved"
exit $LASTEXITCODE
