#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_job_common.sh"

AS_OF_DATE="${AS_OF_DATE:-$(date -u +%F)}"
CMD="cd ${ROOT_DIR} && PYTHONPATH=packages/collectors/src python -m collectors.jobs sync-prices"
run_idempotent_job "price_sync" "$AS_OF_DATE" "$CMD"
