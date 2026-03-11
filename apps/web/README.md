# quant-web

This web app is built with **Next.js** (not Expo/React Native).

## Build / export

Use:

```bash
npm --prefix apps/web run build
```

If you run `npx expo export --platform web`, it will fail because this repository does not contain an Expo project.

## Deploying on Vercel

This repository is a monorepo. For Vercel deployments, point the project at the Next.js app in `apps/web`:

1. Set **Root Directory** to `apps/web` (Project Settings → General).
2. Set **Framework Preset** to **Next.js**.
3. If you keep a root `vercel.json`, use monorepo-aware commands:
   - install: `cd apps/web && npm install`
   - build: `cd apps/web && npm run build`
4. Set `outputDirectory` to `apps/web/.next` to avoid the Vercel default static output expectation (`dist`).

If your project still runs `npx expo export --platform web`, clear any stale custom build command and re-deploy.
If deployment fails with `No Output Directory named "dist" found`, confirm `vercel.json` includes `"outputDirectory": "apps/web/.next"` and redeploy.
If deployment succeeds but the URL shows `404: NOT_FOUND`, check that the domain is attached to the latest production deployment and that Root Directory is still `apps/web`.
