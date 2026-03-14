[CmdletBinding()]
param(
    [string]$TokenFile = 'C:\quant\secrets\cloudflare-tunnel.token'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$BinaryPath = Join-Path $RepoRoot 'tools\cloudflared\cloudflared.exe'
$LogDir = Join-Path $RepoRoot '.logs\cloudflare'
$StdOutLog = Join-Path $LogDir 'cloudflare-tunnel.out.log'
$StdErrLog = Join-Path $LogDir 'cloudflare-tunnel.err.log'

if (-not (Test-Path $BinaryPath)) {
    throw 'cloudflared.exe was not found. Run .\scripts\tunnel\Install-Cloudflared.ps1 first.'
}

if (-not (Test-Path $TokenFile)) {
    throw 'Tunnel token file was not found. Save the Cloudflare dashboard token to C:\quant\secrets\cloudflare-tunnel.token and run this script again.'
}

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$process = Start-Process -FilePath $BinaryPath `
    -ArgumentList @('tunnel', 'run', '--token-file', $TokenFile) `
    -WorkingDirectory $RepoRoot `
    -RedirectStandardOutput $StdOutLog `
    -RedirectStandardError $StdErrLog `
    -Wait `
    -PassThru

exit $process.ExitCode
