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
$LocalScriptsDir = Join-Path (Split-Path $PSScriptRoot -Parent) 'local'
$VenvPython = Join-Path $RepoRoot '.venv\Scripts\python.exe'
$AppDir = Join-Path $RepoRoot 'apps\api\src'
$LogDir = Join-Path $RepoRoot '.logs\ops'
$StdOutLog = Join-Path $LogDir 'backend-production.out.log'
$StdErrLog = Join-Path $LogDir 'backend-production.err.log'

if (-not (Test-Path $VenvPython)) {
    throw 'Python virtual environment was not found. Run .\scripts\local\Setup-LocalDev.ps1 first.'
}

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$StartDbScript = Join-Path $LocalScriptsDir 'Start-LocalDb.ps1'
$RunMigrationsScript = Join-Path $LocalScriptsDir 'Invoke-Migrations.ps1'
$Deadline = (Get-Date).AddSeconds($DockerRetrySeconds)

while ($true) {
    try {
        & $StartDbScript
        break
    } catch {
        if ((Get-Date) -ge $Deadline) {
            throw
        }

        Write-Host 'Waiting for Docker Desktop to become reachable before starting the backend...'
        Start-Sleep -Seconds 5
    }
}

if (-not $SkipMigrations) {
    & $RunMigrationsScript
}

$process = Start-Process -FilePath $VenvPython `
    -ArgumentList @('-m', 'uvicorn', 'api.main:app', '--host', $BindHost, '--port', $Port, '--app-dir', $AppDir) `
    -WorkingDirectory $RepoRoot `
    -RedirectStandardOutput $StdOutLog `
    -RedirectStandardError $StdErrLog `
    -Wait `
    -PassThru

exit $process.ExitCode
