#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="${PY:-python3}"

LEAGUES=(2)
SEASON=2025

FROM_DATE=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --from)
      FROM_DATE="$2"
      shift 2
      ;;
    *)
      echo "Usage: $0 --from YYYY-MM-DD"
      exit 1
      ;;
  esac
done

if [ -z "$FROM_DATE" ]; then
  echo "You must provide --from YYYY-MM-DD"
  exit 1
fi

TODAY=$(date +%Y-%m-%d)

mkdir -p "$SCRIPT_DIR/logs"
LOG_FILE="$SCRIPT_DIR/logs/backfill_$(date +%Y%m%d_%H%M%S).log"

echo "============================================================" | tee -a "$LOG_FILE"
echo "🚀 MANUAL BACKFILL STARTED at $(date)" | tee -a "$LOG_FILE"
echo "   From:  $FROM_DATE" | tee -a "$LOG_FILE"
echo "   Until: $TODAY" | tee -a "$LOG_FILE"
echo "   Leagues: ${LEAGUES[*]}" | tee -a "$LOG_FILE"
echo "============================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

CURRENT="$FROM_DATE"

while [[ "$CURRENT" < "$TODAY" || "$CURRENT" == "$TODAY" ]]; do
  echo "================ DATE: $CURRENT ================" | tee -a "$LOG_FILE"

  for league in "${LEAGUES[@]}"; do
    echo "--- League $league ($CURRENT) ---" | tee -a "$LOG_FILE"

    "$PY" "$SCRIPT_DIR/main.py" \
      --league "$league" \
      --season "$SEASON" \
      --date "$CURRENT" 2>&1 | tee -a "$LOG_FILE"

    echo "" | tee -a "$LOG_FILE"
  done

  if date --version >/dev/null 2>&1; then
    CURRENT=$(date -d "$CURRENT + 1 day" +%Y-%m-%d)
  else
    CURRENT=$(date -j -f "%Y-%m-%d" "$CURRENT" "+%Y-%m-%d" -v+1d)
  fi
done

echo "============================================================" | tee -a "$LOG_FILE"
echo "✅ Backfill completed at $(date)" | tee -a "$LOG_FILE"
echo "============================================================" | tee -a "$LOG_FILE"