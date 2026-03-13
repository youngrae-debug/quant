[CmdletBinding()]
param(
    [string]$BindHost = '0.0.0.0',
    [int]$Port = 8000,
    [switch]$SkipMigrations
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ScriptsDir = (Resolve-Path $PSScriptRoot).Path

& (Join-Path $ScriptsDir 'Start-LocalDb.ps1')

if (-not $SkipMigrations) {
    & (Join-Path $ScriptsDir 'Invoke-Migrations.ps1')
}

& (Join-Path $ScriptsDir 'Start-Api.ps1') -BindHost $BindHost -Port $Port