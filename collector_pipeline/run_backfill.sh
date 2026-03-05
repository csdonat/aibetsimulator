#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="${PY:-python3}"

LEAGUES=(2 39 140 135 78 45 46 61 98 143 137 271 556)
SEASON=2025

FROM_DATE=""
TO_DATE=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --from)
      FROM_DATE="$2"
      shift 2
      ;;
    --to)
      TO_DATE="$2"
      shift 2
      ;;
    *)
      echo "Usage: $0 --from YYYY-MM-DD [--to YYYY-MM-DD]"
      exit 1
      ;;
  esac
done

if [ -z "$FROM_DATE" ]; then
  echo "You must provide --from YYYY-MM-DD"
  exit 1
fi

# If --to is not provided, default to today
if [ -z "$TO_DATE" ]; then
  TO_DATE=$(date +%Y-%m-%d)
fi

mkdir -p "$SCRIPT_DIR/logs"
LOG_FILE="$SCRIPT_DIR/logs/backfill_$(date +%Y%m%d_%H%M%S).log"

echo "============================================================" | tee -a "$LOG_FILE"
echo "🚀 BACKFILL STARTED at $(date)" | tee -a "$LOG_FILE"
echo "   From:  $FROM_DATE" | tee -a "$LOG_FILE"
echo "   To:    $TO_DATE" | tee -a "$LOG_FILE"
echo "   Leagues: ${LEAGUES[*]}" | tee -a "$LOG_FILE"
echo "============================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

for league in "${LEAGUES[@]}"; do
  echo "================ League $league ================" | tee -a "$LOG_FILE"

  "$PY" "$SCRIPT_DIR/main.py" \
    --league "$league" \
    --season "$SEASON" \
    --from "$FROM_DATE" \
    --to "$TO_DATE" 2>&1 | tee -a "$LOG_FILE"

  echo "" | tee -a "$LOG_FILE"
done

echo "============================================================" | tee -a "$LOG_FILE"
echo "✅ Backfill completed at $(date)" | tee -a "$LOG_FILE"
echo "============================================================" | tee -a "$LOG_FILE"