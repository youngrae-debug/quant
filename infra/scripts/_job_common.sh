#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG_DIR="${ROOT_DIR}/var/log/jobs"
RUN_DIR="${ROOT_DIR}/var/run/jobs"
mkdir -p "${LOG_DIR}" "${RUN_DIR}"

job_log() {
  local level="$1"; shift
  local job="$1"; shift
  local message="$1"; shift || true
  local extra="${1:-{}}"
  printf '{"ts":"%s","level":"%s","job":"%s","message":"%s","extra":%s}\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$level" "$job" "$message" "$extra"
}

run_idempotent_job() {
  local job_name="$1"; shift
  local as_of_date="$1"; shift
  local command="$*"

  local lock_file="${RUN_DIR}/${job_name}.lock"
  local marker_file="${RUN_DIR}/${job_name}-${as_of_date}.done"

  exec 9>"${lock_file}"
  if ! flock -n 9; then
    job_log "warning" "$job_name" "job already running; skip" '{"reason":"lock_busy"}'
    return 0
  fi

  if [[ -f "$marker_file" && "${FORCE_RUN:-0}" != "1" ]]; then
    job_log "info" "$job_name" "job already completed for date; skip" "{\"as_of_date\":\"${as_of_date}\"}"
    return 0
  fi

  job_log "info" "$job_name" "job started" "{\"as_of_date\":\"${as_of_date}\"}"
  if eval "$command"; then
    touch "$marker_file"
    job_log "info" "$job_name" "job completed" "{\"as_of_date\":\"${as_of_date}\"}"
    return 0
  fi

  job_log "error" "$job_name" "job failed" "{\"as_of_date\":\"${as_of_date}\"}"
  return 1
}
