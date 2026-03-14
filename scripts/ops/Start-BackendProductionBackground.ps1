[CmdletBinding()]
param(
    [string]$BindHost = '0.0.0.0',
    [int]$Port = 8000,
    [switch]$SkipMigrations,
    [int]$DockerRetrySeconds = 300
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$ScriptPath = Join-Path $PSScriptRoot 'Run-BackendProduction.ps1'

$ArgumentList = @(
    '-ExecutionPolicy', 'Bypass',
    '-File', $ScriptPath,
    '-BindHost', $BindHost,
    '-Port', $Port,
    '-DockerRetrySeconds', $DockerRetrySeconds
)

if ($SkipMigrations) {
    $ArgumentList += '-SkipMigrations'
}

$process = Start-Process -FilePath 'powershell.exe' `
    -ArgumentList $ArgumentList `
    -WorkingDirectory $RepoRoot `
    -PassThru

$process.Id
