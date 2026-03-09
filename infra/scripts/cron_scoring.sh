#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_job_common.sh"

AS_OF_DATE="${AS_OF_DATE:-$(date -u +%F)}"
CMD="cd ${ROOT_DIR} && PYTHONPATH=apps/api/src:packages/quant-engine/src python -m api.jobs score --as-of-date ${AS_OF_DATE}"
run_idempotent_job "scoring" "$AS_OF_DATE" "$CMD"
