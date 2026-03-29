# Copyright (c) 2025 Oleksandr Tishchenko / Marketing America Corp
param(
  [string]$Root = ".",
  [string]$Domain = "canon",
  [string]$Dir = ""
)
$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path -Path $Root

$cmd = @("--root", $repoRoot, "--domain", $Domain)
if ($Dir -ne "") { $cmd += @("--dir", $Dir) }

node (Join-Path $repoRoot "owner/lint/doc-name-check.js") @cmd
exit $LASTEXITCODE
