[CmdletBinding()]
param(
  [Parameter(Mandatory = $false)]
  [string] $RepoRoot = ".",

  [Parameter(Mandatory = $false)]
  [string] $ProposalPath = ".report/gate-fix-proposal.ndjson",

  [Parameter(Mandatory = $false)]
  [switch] $ApplySafe,

  [Parameter(Mandatory = $false)]
  [switch] $PrintOnly,

  [Parameter(Mandatory = $false)]
  [switch] $AllowDangerous
)

$ErrorActionPreference = "Stop"

function Resolve-RepoPath([string]$p) {
  $root = (Resolve-Path -LiteralPath $RepoRoot).Path
  if ([string]::IsNullOrWhiteSpace($p)) { return $root }
  return (Join-Path $root $p)
}

function Ensure-Dir([string]$dirPath) {
  if ([string]::IsNullOrWhiteSpace($dirPath)) { return }
  if (!(Test-Path -LiteralPath $dirPath)) {
    New-Item -ItemType Directory -Path $dirPath | Out-Null
  }
}

function Get-Sha256([string]$filePath) {
  if (!(Test-Path -LiteralPath $filePath)) { return "" }
  return (Get-FileHash -LiteralPath $filePath -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Print-Op($p) {
  $note = ""
  if ($p.PSObject.Properties.Name -contains "note") { $note = [string]$p.note }
  $lvl = ""
  if ($p.PSObject.Properties.Name -contains "level") { $lvl = [string]$p.level }
  Write-Host ("[gate] proposal op={0} level={1} note={2}" -f $p.op, $lvl, $note)
}

function Is-SafeOp($p) {
  $op = [string]$p.op
  switch ($op) {
    "file.append_lines" { return $true }
    "file.ensure_exists" { return $true }
    "path.ensure_dir" { return $true }
    "chmod.add_x" { return $true }
    "report.print" { return $true }
    "file.write_text" {
      if ($p.PSObject.Properties.Name -contains "guard") {
        return ([string]$p.guard) -eq "missing_only"
      }
      return $false
    }
    default { return $false }
  }
}

function Apply-FileAppendLines($p) {
  $path = Resolve-RepoPath $p.path
  $dir = Split-Path -Parent $path
  Ensure-Dir $dir

  if (!(Test-Path -LiteralPath $path)) {
    New-Item -ItemType File -Path $path | Out-Null
  }

  $cur = @()
  try { $cur = Get-Content -LiteralPath $path -ErrorAction SilentlyContinue } catch { $cur = @() }

  $need = @()
  foreach ($x in $p.lines) {
    $s = [string]$x
    if ($cur -notcontains $s) { $need += $s }
  }

  if ($need.Count -gt 0) {
    Add-Content -LiteralPath $path -Value "`n# gate: append_lines`n"
    Add-Content -LiteralPath $path -Value ($need -join "`n")
    Write-Host ("[gate] applied file.append_lines path={0} added={1}" -f $p.path, $need.Count)
  } else {
    Write-Host ("[gate] noop file.append_lines path={0}" -f $p.path)
  }
}

function Apply-FileEnsureExists($p) {
  $path = Resolve-RepoPath $p.path
  $dir = Split-Path -Parent $path
  Ensure-Dir $dir

  if (!(Test-Path -LiteralPath $path)) {
    New-Item -ItemType File -Path $path | Out-Null
    Write-Host ("[gate] applied file.ensure_exists path={0}" -f $p.path)
  } else {
    Write-Host ("[gate] noop file.ensure_exists path={0}" -f $p.path)
  }
}

function Apply-FileReplaceRegex($p) {
  $path = Resolve-RepoPath $p.path
  if (!(Test-Path -LiteralPath $path)) {
    Write-Host ("[gate] skip file.replace_regex (missing) path={0}" -f $p.path)
    return
  }

  $content = Get-Content -LiteralPath $path -Raw
  $pattern = [string]$p.pattern
  $replacement = [string]$p.replacement
  $newContent = [regex]::Replace($content, $pattern, $replacement)

  if ($newContent -ne $content) {
    Set-Content -LiteralPath $path -Value $newContent -NoNewline
    Write-Host ("[gate] applied file.replace_regex path={0}" -f $p.path)
  } else {
    Write-Host ("[gate] noop file.replace_regex path={0}" -f $p.path)
  }
}

function Apply-FileWriteText($p) {
  $path = Resolve-RepoPath $p.path
  $dir = Split-Path -Parent $path
  Ensure-Dir $dir

  $guard = ""
  if ($p.PSObject.Properties.Name -contains "guard") { $guard = [string]$p.guard }

  if ($guard -eq "missing_only") {
    if (Test-Path -LiteralPath $path) {
      Write-Host ("[gate] skip file.write_text (exists, missing_only) path={0}" -f $p.path)
      return
    }
    Set-Content -LiteralPath $path -Value ([string]$p.text) -NoNewline
    Write-Host ("[gate] applied file.write_text (missing_only) path={0}" -f $p.path)
    return
  }

  if ($guard -eq "sha256") {
    $expected = ""
    if ($p.PSObject.Properties.Name -contains "expected") { $expected = ([string]$p.expected).ToLowerInvariant() }
    $actual = Get-Sha256 $path

    if ($actual -ne $expected) {
      Write-Host ("[gate] skip file.write_text (sha256 mismatch) path={0}" -f $p.path)
      return
    }
    Set-Content -LiteralPath $path -Value ([string]$p.text) -NoNewline
    Write-Host ("[gate] applied file.write_text (sha256 ok) path={0}" -f $p.path)
    return
  }

  Set-Content -LiteralPath $path -Value ([string]$p.text) -NoNewline
  Write-Host ("[gate] applied file.write_text (unguarded) path={0}" -f $p.path)
}

function Apply-FileDelete($p) {
  $path = Resolve-RepoPath $p.path
  if (Test-Path -LiteralPath $path) {
    Remove-Item -LiteralPath $path -Force -Recurse
    Write-Host ("[gate] applied file.delete path={0}" -f $p.path)
  } else {
    Write-Host ("[gate] noop file.delete path={0}" -f $p.path)
  }
}

function Apply-PathEnsureDir($p) {
  $path = Resolve-RepoPath $p.path
  Ensure-Dir $path
  Write-Host ("[gate] applied path.ensure_dir path={0}" -f $p.path)
}

function Apply-PathMove($p) {
  $from = Resolve-RepoPath $p.from
  $to = Resolve-RepoPath $p.to
  $overwrite = $false
  if ($p.PSObject.Properties.Name -contains "overwrite") { $overwrite = [bool]$p.overwrite }

  if (!(Test-Path -LiteralPath $from)) {
    Write-Host ("[gate] skip path.move (missing from) from={0}" -f $p.from)
    return
  }

  if ((Test-Path -LiteralPath $to) -and (-not $overwrite)) {
    Write-Host ("[gate] skip path.move (target exists, overwrite=false) to={0}" -f $p.to)
    return
  }

  $toDir = Split-Path -Parent $to
  Ensure-Dir $toDir

  Move-Item -LiteralPath $from -Destination $to -Force:$overwrite
  Write-Host ("[gate] applied path.move from={0} to={1}" -f $p.from, $p.to)
}

function Apply-PathRename($p) {
  Apply-PathMove ([pscustomobject]@{
    from = $p.from
    to = $p.to
    overwrite = $false
  })
}

function Apply-ChmodAddX($p) {
  $pathRel = [string]$p.path
  $path = Resolve-RepoPath $pathRel

  if (!(Test-Path -LiteralPath $path)) {
    Write-Host ("[gate] skip chmod.add_x (missing) path={0}" -f $pathRel)
    return
  }

  if (-not $IsWindows) {
    & chmod +x -- $path | Out-Null
    Write-Host ("[gate] applied chmod.add_x path={0}" -f $pathRel)
    return
  }

  $git = Get-Command git -ErrorAction SilentlyContinue
  if ($null -ne $git) {
    & git update-index --chmod=+x -- $pathRel | Out-Null
    Write-Host ("[gate] applied chmod.add_x via git-index path={0}" -f $pathRel)
  } else {
    Write-Host ("[gate] skip chmod.add_x on Windows (git not found) path={0}" -f $pathRel)
  }
}

function Apply-ReportPrint($p) {
  Write-Host ("[gate] proposal: {0}" -f ([string]$p.text))
}

$proposalFile = Resolve-RepoPath $ProposalPath
if (!(Test-Path -LiteralPath $proposalFile)) {
  Write-Host "[gate] no proposal file: $ProposalPath"
  exit 0
}

$lines = Get-Content -LiteralPath $proposalFile | Where-Object { $_.Trim().Length -gt 0 }
Write-Host ("[gate] proposal file: {0} entries={1}" -f $ProposalPath, $lines.Count)

foreach ($line in $lines) {
  $p = $null
  try { $p = $line | ConvertFrom-Json } catch {
    Write-Host "[gate] skip bad json line"
    continue
  }

  if ($null -eq $p.op) {
    Write-Host "[gate] skip proposal without op"
    continue
  }

  Print-Op $p

  $shouldApply = $false
  if ($PrintOnly) { $shouldApply = $false }
  elseif ($ApplySafe) { $shouldApply = (Is-SafeOp $p) }
  elseif ($AllowDangerous) { $shouldApply = $true }
  else { $shouldApply = $false }

  if (-not $shouldApply) {
    continue
  }

  switch ([string]$p.op) {
    "file.append_lines" { Apply-FileAppendLines $p }
    "file.ensure_exists" { Apply-FileEnsureExists $p }
    "file.replace_regex" { Apply-FileReplaceRegex $p }
    "file.write_text" { Apply-FileWriteText $p }
    "file.delete" { Apply-FileDelete $p }
    "path.ensure_dir" { Apply-PathEnsureDir $p }
    "path.move" { Apply-PathMove $p }
    "path.rename" { Apply-PathRename $p }
    "chmod.add_x" { Apply-ChmodAddX $p }
    "report.print" { Apply-ReportPrint $p }
    "agent.required" {
      Write-Host ("[gate] agent.required prompt={0}" -f ([string]$p.prompt))
    }
    default {
      Write-Host ("[gate] unknown op={0} (skip)" -f ([string]$p.op))
    }
  }
}
