[CmdletBinding()]
param(
    [int]$TimeoutSeconds = 120
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path

docker version *> $null
if ($LASTEXITCODE -ne 0) {
    throw 'Docker Engine is not reachable. Start Docker Desktop, wait until it is ready, then run .\scripts\local\Start-LocalDb.ps1 again.'
}

Push-Location $RepoRoot
try {
    docker compose up -d db
    if ($LASTEXITCODE -ne 0) {
        throw 'docker compose up -d db failed. Confirm Docker Desktop is running and reachable.'
    }
} finally {
    Pop-Location
}

$Deadline = (Get-Date).AddSeconds($TimeoutSeconds)
while ((Get-Date) -lt $Deadline) {
    $Health = docker inspect --format '{{.State.Health.Status}}' quant-db 2>$null
    if ($LASTEXITCODE -eq 0 -and $Health.Trim() -eq 'healthy') {
        Write-Host 'PostgreSQL is healthy on localhost:5432.'
        return
    }

    Start-Sleep -Seconds 2
}

throw "quant-db did not become healthy within $TimeoutSeconds seconds."