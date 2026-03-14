[CmdletBinding()]
param(
    [string]$AsOfDate = (Get-Date -Format 'yyyy-MM-dd'),
    [int]$SicLimit = 0,
    [int]$SymbolInfoLimit = 2000,
    [int]$FilingLimit = 500,
    [int]$PriceLimit = 200,
    [int]$DockerRetrySeconds = 300
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$LogDir = Join-Path $RepoRoot '.logs\ops'
$LockFile = Join-Path $LogDir 'data-pipeline.lock'
$LogStamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$StdOutLog = Join-Path $LogDir ("data-pipeline-{0}.out.log" -f $LogStamp)
$StdErrLog = Join-Path $LogDir ("data-pipeline-{0}.err.log" -f $LogStamp)
$PipelineScript = Join-Path $RepoRoot 'scripts\local\Run-DataPipeline.ps1'
$StartDbScript = Join-Path $RepoRoot 'scripts\local\Start-LocalDb.ps1'

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

if (Test-Path $LockFile) {
    $ExistingPid = (Get-Content $LockFile -ErrorAction SilentlyContinue | Select-Object -First 1)
    if ($ExistingPid -match '^\d+$') {
        try {
            Get-Process -Id ([int]$ExistingPid) -ErrorAction Stop | Out-Null
            Write-Output "Data pipeline is already running under PID $ExistingPid."
            exit 0
        } catch {
            Remove-Item $LockFile -Force -ErrorAction SilentlyContinue
        }
    } else {
        Remove-Item $LockFile -Force -ErrorAction SilentlyContinue
    }
}

Set-Content -Path $LockFile -Value $PID -Encoding ascii
$ExitCode = 1

try {
    $Deadline = (Get-Date).AddSeconds($DockerRetrySeconds)
    while ($true) {
        try {
            & $StartDbScript
            break
        } catch {
            if ((Get-Date) -ge $Deadline) {
                throw
            }

            Write-Host 'Waiting for Docker Desktop to become reachable before running the data pipeline...'
            Start-Sleep -Seconds 5
        }
    }

    @(
        "[{0}] Starting production data pipeline" -f (Get-Date -Format s),
        "AsOfDate=$AsOfDate SicLimit=$SicLimit SymbolInfoLimit=$SymbolInfoLimit FilingLimit=$FilingLimit PriceLimit=$PriceLimit"
    ) | Set-Content -Path $StdOutLog -Encoding utf8

    $Process = Start-Process -FilePath 'powershell.exe' `
        -ArgumentList @(
            '-ExecutionPolicy', 'Bypass',
            '-File', $PipelineScript,
            '-AsOfDate', $AsOfDate,
            '-SicLimit', $SicLimit,
            '-SymbolInfoLimit', $SymbolInfoLimit,
            '-FilingLimit', $FilingLimit,
            '-PriceLimit', $PriceLimit
        ) `
        -WorkingDirectory $RepoRoot `
        -RedirectStandardOutput $StdOutLog `
        -RedirectStandardError $StdErrLog `
        -Wait `
        -PassThru

    $ExitCode = $Process.ExitCode
    Add-Content -Path $StdOutLog -Value ("[{0}] Pipeline exit code: {1}" -f (Get-Date -Format s), $ExitCode)
} catch {
    $_ | Out-String | Add-Content -Path $StdErrLog
    throw
} finally {
    Remove-Item $LockFile -Force -ErrorAction SilentlyContinue
}

exit $ExitCode
