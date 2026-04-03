Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = Resolve-Path (Join-Path $PSScriptRoot '..')
Set-Location $root

python tools/build_antora_site.py
npx antora antora-playbook.yml --fetch
