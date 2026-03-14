[CmdletBinding()]
param(
    [string]$TaskPrefix = 'Quant'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$TaskNames = @(
    "$TaskPrefix Backend Startup",
    "$TaskPrefix Tunnel Startup",
    "$TaskPrefix Daily Pipeline"
)

foreach ($TaskName in $TaskNames) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
}
