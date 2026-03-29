# Copyright (c) 2025 Oleksandr Tishchenko / Marketing America Corp
param(
  [Parameter(Mandatory = $true)]
  [string]$ZipPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $ZipPath)) {
  throw "ZIP not found: $ZipPath"
}

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$zip = [System.IO.Compression.ZipFile]::OpenRead($ZipPath)
try {
  $top = New-Object System.Collections.Generic.HashSet[string]

  foreach ($e in $zip.Entries) {
    if ([string]::IsNullOrWhiteSpace($e.FullName)) { continue }

    # Normalize to forward slashes.
    $name = $e.FullName.Replace('\\', '/').TrimStart('/')
    if ($name.Length -eq 0) { continue }

    # Skip pure directory entries.
    if ($name.EndsWith('/')) { continue }

    $first = $name.Split('/')[0]
    if ($first.Length -eq 0) { continue }

    [void]$top.Add($first)
  }

  if ($top.Count -le 0) {
    throw "ZIP appears empty: $ZipPath"
  }

  if ($top.Count -eq 1) {
    $only = ($top | Select-Object -First 1)
    throw "ZIP has a single top-level entry '$only'. This looks like a wrapper folder. Put project files/folders at the ZIP root (flat-root)."
  }

  Write-Host "OK: flat-root ($($top.Count) top-level entries)"
}
finally {
  $zip.Dispose()
}
