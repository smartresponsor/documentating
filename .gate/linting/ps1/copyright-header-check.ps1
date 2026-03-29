# Copyright (c) 2025 Oleksandr Tishchenko / Marketing America Corp
param(
  [string]$Root = "."
)

$ErrorActionPreference = "Stop"

$Header = "Copyright (c) 2025 Oleksandr Tishchenko / Marketing America Corp"
$IgnoreDir = @(".git","node_modules","vendor","var","build","dist",".idea",".vscode","cache","fixture")
$Ext = @(".php",".js",".ts",".tsx",".sh",".ps1")

$script:bad = 0
Get-ChildItem -Path $Root -Recurse -File | ForEach-Object {
  foreach ($ig in $IgnoreDir) {
    $needle = [System.IO.Path]::DirectorySeparatorChar + $ig + [System.IO.Path]::DirectorySeparatorChar
    if ($_.FullName -like ("*" + $needle + "*")) {
      return
    }
  }

  if ($Ext -notcontains $_.Extension) { return }

  $head = Get-Content -Path $_.FullName -TotalCount 10 -ErrorAction SilentlyContinue
  if (-not ($head -join "`n").Contains($Header)) {
    Write-Output ("missing header: " + $_.FullName)
    $script:bad = $script:bad + 1
  }
}

if ($script:bad -gt 0) {
  Write-Error ("FAIL: {0} file(s) missing copyright header." -f $script:bad)
  exit 2
}
Write-Output "OK: header present."
