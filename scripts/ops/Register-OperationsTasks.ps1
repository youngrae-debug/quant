[CmdletBinding()]
param(
    [ValidatePattern('^\d{2}:\d{2}$')]
    [string]$DailyBatchTime = '07:10',
    [string]$TaskPrefix = 'Quant',
    [switch]$StartAfterRegister
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$CurrentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$DailyAt = [datetime]::Today.Add([timespan]::Parse($DailyBatchTime))

$Principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive -RunLevel Highest
$StartupSettings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew `
    -StartWhenAvailable
$BatchSettings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Hours 12) `
    -MultipleInstances IgnoreNew `
    -StartWhenAvailable

$BackendTaskName = "$TaskPrefix Backend Startup"
$TunnelTaskName = "$TaskPrefix Tunnel Startup"
$PipelineTaskName = "$TaskPrefix Daily Pipeline"

$BackendAction = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-ExecutionPolicy Bypass -File `"$RepoRoot\scripts\ops\Run-BackendProduction.ps1`""
$TunnelAction = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-ExecutionPolicy Bypass -File `"$RepoRoot\scripts\ops\Run-CloudflareTunnel.ps1`""
$PipelineAction = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-ExecutionPolicy Bypass -File `"$RepoRoot\scripts\ops\Run-DataPipelineProduction.ps1`""

try {
    Register-ScheduledTask `
        -TaskName $BackendTaskName `
        -Action $BackendAction `
        -Trigger (New-ScheduledTaskTrigger -AtLogOn) `
        -Description 'Starts the local FastAPI backend for production-style operation.' `
        -Principal $Principal `
        -Settings $StartupSettings `
        -Force | Out-Null

    Register-ScheduledTask `
        -TaskName $TunnelTaskName `
        -Action $TunnelAction `
        -Trigger (New-ScheduledTaskTrigger -AtLogOn) `
        -Description 'Starts the Cloudflare Tunnel used by the public frontend.' `
        -Principal $Principal `
        -Settings $StartupSettings `
        -Force | Out-Null

    Register-ScheduledTask `
        -TaskName $PipelineTaskName `
        -Action $PipelineAction `
        -Trigger (New-ScheduledTaskTrigger -Daily -At $DailyAt) `
        -Description 'Runs the daily production data pipeline for the local backend.' `
        -Principal $Principal `
        -Settings $BatchSettings `
        -Force | Out-Null
} catch {
    throw 'Scheduled task registration requires an elevated PowerShell session. Re-run .\scripts\ops\Register-OperationsTasks.ps1 from PowerShell as Administrator.'
}

if ($StartAfterRegister) {
    Start-ScheduledTask -TaskName $BackendTaskName
    Start-ScheduledTask -TaskName $TunnelTaskName
}

Write-Output "Registered scheduled tasks for ${CurrentUser}:"
Write-Output "- $BackendTaskName (At logon)"
Write-Output "- $TunnelTaskName (At logon)"
Write-Output "- $PipelineTaskName (Daily at $DailyBatchTime)"
