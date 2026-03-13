[CmdletBinding()]
param(
    [string]$AsOfDate = (Get-Date -Format 'yyyy-MM-dd'),
    [int]$SicLimit = 200,
    [int]$SymbolInfoLimit = 500,
    [int]$FilingLimit = 100,
    [int]$PriceLimit = 50
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$VenvPython = Join-Path $RepoRoot '.venv\Scripts\python.exe'

if (-not (Test-Path $VenvPython)) {
    throw 'Python virtual environment was not found. Run .\scripts\local\Setup-LocalDev.ps1 first.'
}

Push-Location (Join-Path $RepoRoot 'packages\collectors')
try {
    & $VenvPython -m collectors.jobs sync-sec-symbols --sic-limit $SicLimit
    & $VenvPython -m collectors.jobs sync-symbol-info --max-symbols $SymbolInfoLimit
    & $VenvPython -m collectors.jobs sync-filings --max-symbols $FilingLimit
    & $VenvPython -m collectors.jobs sync-prices --max-symbols $PriceLimit
    & $VenvPython -m collectors.jobs materialize-fundamentals --as-of-date $AsOfDate
} finally {
    Pop-Location
}

Push-Location (Join-Path $RepoRoot 'apps\api')
try {
    & $VenvPython -m api.jobs score --as-of-date $AsOfDate
    & $VenvPython -m api.jobs refresh-recommendations --as-of-date $AsOfDate
} finally {
    Pop-Location
}
