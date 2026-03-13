# Cloudflare Tunnel Guide

## Target architecture

You want this split:

- Frontend: Vercel
- Backend: your local PC
- Public backend hostname: `api.wearethesecret.com`
- Tunnel path: `api.wearethesecret.com -> Cloudflare Tunnel -> http://localhost:8000`

This repository is now prepared for that layout.

## What is already ready

- local API server is running on `http://localhost:8000`
- local database is running on `localhost:5432`
- `cloudflared` binary is installed at `tools/cloudflared/cloudflared.exe`
- backend CORS template now includes:
  - `http://localhost:3000`
  - `https://wearethesecret.com`
  - `https://www.wearethesecret.com`

## 1. Update local backend CORS

Make sure `apps/api/.env` contains:

```env
CORS_ORIGINS=http://localhost:3000,https://wearethesecret.com,https://www.wearethesecret.com
```

If you change that file while the API is running, restart the backend.

## 2. Create the Cloudflare Tunnel in the dashboard

Because `wearethesecret.com` already uses Cloudflare nameservers, use a named tunnel.

In Cloudflare Zero Trust:

1. Go to **Networks > Tunnels**
2. Create a **Cloudflared** tunnel
3. Use a name like `wearethesecret-local-api`
4. When Cloudflare shows the connector setup step, copy the tunnel token

Official references:

- [Install cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)
- [Route traffic with a tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/routing-to-tunnel/)
- [Run tunnel with token](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/configure-tunnels/remote-tunnel-permissions/)

## 3. Save the tunnel token locally

Create this file:

`C:\quant\secrets\cloudflare-tunnel.token`

Its content should be the token value only.

Example:

```text
eyJhIjoi...redacted...
```

That path is already ignored by Git.

## 4. Add the public hostname

Inside the same Cloudflare Tunnel configuration, create a public hostname:

- Subdomain: `api`
- Domain: `wearethesecret.com`
- Type: `HTTP`
- URL: `localhost:8000`

Final public URL:

- `https://api.wearethesecret.com`

## 5. Start the local tunnel

Foreground mode:

```powershell
.\scripts\tunnel\Start-CloudflareTunnel.ps1
```

Background mode:

```powershell
.\scripts\tunnel\Start-CloudflareTunnelBackground.ps1
```

Background logs:

- `C:\quant\.logs\cloudflare\cloudflare-tunnel.out.log`
- `C:\quant\.logs\cloudflare\cloudflare-tunnel.err.log`

## 6. Point Vercel frontend to the local backend

In Vercel project settings, change:

```env
NEXT_PUBLIC_API_URL=https://api.wearethesecret.com
```

After that, redeploy the frontend.

## 7. Recommended run order

On your PC:

1. `.\scripts\local\Start-LocalDb.ps1`
2. `.\scripts\local\Start-Backend.ps1`
3. `.\scripts\tunnel\Start-CloudflareTunnel.ps1`

On Vercel:

1. update `NEXT_PUBLIC_API_URL`
2. redeploy

## Verification

Check these in order:

1. `http://localhost:8000/health`
2. `https://api.wearethesecret.com/health`
3. `https://www.wearethesecret.com`

Expected backend health response:

```json
{"status":"ok"}
```

## Important notes

- If your PC is off, sleeping, or your internet changes, the backend becomes unreachable.
- This is workable for personal or low-traffic use, but it is not equivalent to managed hosting.
- For production stability later, a VPS or managed backend host will still be safer.
