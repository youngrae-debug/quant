[CmdletBinding()]
param(
    [string]$TokenFile = 'C:\quant\secrets\cloudflare-tunnel.token'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$LogDir = Join-Path $RepoRoot '.logs\cloudflare'
$ScriptPath = Join-Path $RepoRoot 'scripts\ops\Run-CloudflareTunnel.ps1'

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$process = Start-Process -FilePath 'powershell.exe' `
    -ArgumentList @('-ExecutionPolicy', 'Bypass', '-File', $ScriptPath, '-TokenFile', $TokenFile) `
    -WorkingDirectory $RepoRoot `
    -PassThru

$process.Id
