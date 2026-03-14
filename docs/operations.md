# Local Operations Guide

This document describes the production-style workflow for running the backend from a local Windows PC while the frontend stays on Vercel.

## What this setup does

- keeps `https://www.wearethesecret.com` on Vercel
- serves the backend from your PC through `https://api.wearethesecret.com`
- refreshes data daily through a scheduled Windows task

## Runtime scripts

Foreground backend:

```powershell
.\scripts\ops\Run-BackendProduction.ps1
```

Background backend:

```powershell
.\scripts\ops\Start-BackendProductionBackground.ps1
```

Foreground Cloudflare Tunnel:

```powershell
.\scripts\ops\Run-CloudflareTunnel.ps1
```

Production data pipeline:

```powershell
.\scripts\ops\Run-DataPipelineProduction.ps1
```

The production data pipeline keeps the development script intact and simply uses higher default limits:

- `SicLimit=0`
- `SymbolInfoLimit=2000`
- `FilingLimit=500`
- `PriceLimit=200`

`SicLimit=0` means the daily batch skips the slower SIC backfill step. Raise it only when you want to refresh missing SIC metadata.

Adjust the other values if the machine can handle a wider refresh window.

## Logs

- backend stdout: `C:\quant\.logs\ops\backend-production.out.log`
- backend stderr: `C:\quant\.logs\ops\backend-production.err.log`
- pipeline stdout: `C:\quant\.logs\ops\data-pipeline-*.out.log`
- pipeline stderr: `C:\quant\.logs\ops\data-pipeline-*.err.log`
- tunnel stdout: `C:\quant\.logs\cloudflare\cloudflare-tunnel.out.log`
- tunnel stderr: `C:\quant\.logs\cloudflare\cloudflare-tunnel.err.log`

The production pipeline also uses a lock file at `C:\quant\.logs\ops\data-pipeline.lock` to avoid overlapping runs.

## Register scheduled tasks

Recommended daily batch time for a Korea-based PC is after the US market close data is available:

```powershell
.\scripts\ops\Register-OperationsTasks.ps1 -DailyBatchTime 07:10
```

Run that command from PowerShell as Administrator.

That creates three tasks for the current Windows user:

- `Quant Backend Startup`
- `Quant Tunnel Startup`
- `Quant Daily Pipeline`

Notes:

- these tasks use `Interactive` logon, so the Windows user session should remain signed in
- Docker Desktop should be allowed to start automatically with Windows
- the backend task retries Docker startup for up to 5 minutes before failing

To remove the tasks later:

```powershell
.\scripts\ops\Unregister-OperationsTasks.ps1
```
