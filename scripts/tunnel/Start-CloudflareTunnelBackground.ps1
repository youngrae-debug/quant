[CmdletBinding()]
param(
    [string]$TokenFile = 'C:\quant\secrets\cloudflare-tunnel.token'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$LogDir = Join-Path $RepoRoot '.logs\cloudflare'
$ScriptPath = Join-Path $RepoRoot 'scripts\tunnel\Start-CloudflareTunnel.ps1'

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$process = Start-Process -FilePath 'powershell.exe' `
    -ArgumentList @('-ExecutionPolicy', 'Bypass', '-File', $ScriptPath, '-TokenFile', $TokenFile) `
    -WorkingDirectory $RepoRoot `
    -RedirectStandardOutput (Join-Path $LogDir 'cloudflare-tunnel.out.log') `
    -RedirectStandardError (Join-Path $LogDir 'cloudflare-tunnel.err.log') `
    -PassThru

$process.Id
