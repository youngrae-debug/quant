[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path

Push-Location (Join-Path $RepoRoot 'apps\web')
try {
    npm.cmd run dev
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: npm.cmd run dev"
    }
} finally {
    Pop-Location
}