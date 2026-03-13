[CmdletBinding()]
param(
    [switch]$SkipNodeInstall,
    [switch]$SkipPythonInstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$VenvPath = Join-Path $RepoRoot '.venv'
$VenvPython = Join-Path $VenvPath 'Scripts\python.exe'
$PipCacheDir = Join-Path $RepoRoot '.pip-cache'
$NpmCacheDir = Join-Path $RepoRoot '.npm-cache'

function Copy-IfMissing {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Source,
        [Parameter(Mandatory = $true)]
        [string]$Destination
    )

    if (-not (Test-Path $Destination)) {
        Copy-Item -Path $Source -Destination $Destination
        Write-Host "Created $Destination"
        return
    }

    Write-Host "Kept existing $Destination"
}

function Invoke-Native {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [string[]]$Arguments = @()
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $FilePath $($Arguments -join ' ')"
    }
}

Copy-IfMissing -Source (Join-Path $RepoRoot '.env.example') -Destination (Join-Path $RepoRoot '.env')
Copy-IfMissing -Source (Join-Path $RepoRoot 'apps\api\.env.example') -Destination (Join-Path $RepoRoot 'apps\api\.env')
Copy-IfMissing -Source (Join-Path $RepoRoot 'apps\web\.env.example') -Destination (Join-Path $RepoRoot 'apps\web\.env.local')
Copy-IfMissing -Source (Join-Path $RepoRoot 'packages\collectors\.env.example') -Destination (Join-Path $RepoRoot 'packages\collectors\.env')

if (-not $SkipPythonInstall) {
    Get-Command py -ErrorAction Stop | Out-Null
    New-Item -ItemType Directory -Force -Path $PipCacheDir | Out-Null
    $env:PIP_CACHE_DIR = $PipCacheDir

    if (-not (Test-Path $VenvPython)) {
        Invoke-Native -FilePath 'py' -Arguments @('-3', '-m', 'venv', $VenvPath)
    }

    Invoke-Native -FilePath $VenvPython -Arguments @('-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools', 'wheel')
    Invoke-Native -FilePath $VenvPython -Arguments @('-m', 'pip', 'install', '-e', (Join-Path $RepoRoot 'packages\quant-engine'), '-e', (Join-Path $RepoRoot 'packages\collectors'), '-e', (Join-Path $RepoRoot 'apps\api'))
} else {
    Write-Host 'Skipped Python dependency installation.'
}

if (-not $SkipNodeInstall) {
    New-Item -ItemType Directory -Force -Path $NpmCacheDir | Out-Null
    Push-Location $RepoRoot
    try {
        npm.cmd install --cache $NpmCacheDir
        if ($LASTEXITCODE -ne 0) {
            throw "Command failed with exit code ${LASTEXITCODE}: npm.cmd install --cache $NpmCacheDir"
        }
    } finally {
        Pop-Location
    }
} else {
    Write-Host 'Skipped Node.js dependency installation.'
}

Write-Host ''
Write-Host 'Local development bootstrap finished.'
Write-Host 'Next steps:'
Write-Host '  1. .\scripts\local\Start-LocalDb.ps1'
Write-Host '  2. .\scripts\local\Invoke-Migrations.ps1'
Write-Host '  3. .\scripts\local\Start-Backend.ps1'
Write-Host '  4. .\scripts\local\Start-Web.ps1'