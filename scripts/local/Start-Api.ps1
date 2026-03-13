[CmdletBinding()]
param(
    [string]$BindHost = '0.0.0.0',
    [int]$Port = 8000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$VenvPython = Join-Path $RepoRoot '.venv\Scripts\python.exe'
$AppDir = Join-Path $RepoRoot 'apps\api\src'

if (-not (Test-Path $VenvPython)) {
    throw 'Python virtual environment was not found. Run .\scripts\local\Setup-LocalDev.ps1 first.'
}

& $VenvPython -m uvicorn api.main:app --host $BindHost --port $Port --reload --app-dir $AppDir --reload-dir $AppDir