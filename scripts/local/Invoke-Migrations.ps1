[CmdletBinding()]
param(
    [string]$Revision = 'head'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$VenvPython = Join-Path $RepoRoot '.venv\Scripts\python.exe'

if (-not (Test-Path $VenvPython)) {
    throw 'Python virtual environment was not found. Run .\scripts\local\Setup-LocalDev.ps1 first.'
}

Push-Location (Join-Path $RepoRoot 'apps\api')
try {
    & $VenvPython -m alembic upgrade $Revision
} finally {
    Pop-Location
}
