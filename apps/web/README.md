# quant-web

This web app is built with **Next.js** (not Expo/React Native).

## Build / export

Use:

```bash
npm --prefix apps/web run build
```

If you run `npx expo export --platform web`, it will fail because this repository does not contain an Expo project.

## Deploying on Vercel

This repository is a monorepo, so the Web app build must point at the Next.js app in `apps/web`.
A root `vercel.json` is included to force the correct commands and avoid Expo defaults:

- install: `npm --prefix apps/web install`
- build: `npm --prefix apps/web run build`
- framework: `nextjs`

If your Vercel project still runs `npx expo export --platform web`, update the project
Framework Preset to **Next.js** and clear any old custom Build Command.
