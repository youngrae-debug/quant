#!/usr/bin/env bash
set -euo pipefail

cp -n .env.example .env || true
cp -n apps/api/.env.example apps/api/.env || true
cp -n apps/web/.env.example apps/web/.env || true
cp -n packages/collectors/.env.example packages/collectors/.env || true
cp -n packages/quant-engine/.env.example packages/quant-engine/.env || true

echo "Environment files bootstrapped."
