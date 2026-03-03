#!/usr/bin/env bash
#
# Daily Incremental Data Collection Script
# Uses existing main.py with --date parameter
#
# Usage:
#   ./run_daily.sh                    # Run for yesterday
#   ./run_daily.sh --date 2025-03-01  # Run for specific date
#
# Cron setup (run daily at 2 AM):
#   0 2 * * * /path/to/collector_pipeline/run_daily.sh >> /path/to/logs/daily.log 2>&1
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="${PY:-python3}"

# --- CONFIGURATION ---
# Configure your leagues here
LEAGUES=(39 140 2)  # Premier League, La Liga, Champions League
SEASON=2025

# --- PARSE ARGUMENTS ---
SPECIFIC_DATE=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --date)
      SPECIFIC_DATE="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--date YYYY-MM-DD]"
      exit 1
      ;;
  esac
done

# --- CALCULATE DATE ---
if [ -z "$SPECIFIC_DATE" ]; then
  # Cross-platform yesterday
  if date --version >/dev/null 2>&1; then
    DATE=$(date -d "yesterday" +%Y-%m-%d)
  else
    DATE=$(date -v-1d +%Y-%m-%d)
  fi
else
  DATE="$SPECIFIC_DATE"
fi

# --- LOGGING ---
mkdir -p "$SCRIPT_DIR/logs"
LOG_FILE="$SCRIPT_DIR/logs/daily_$(date +%Y%m%d_%H%M%S).log"

echo "================================================================================" | tee -a "$LOG_FILE"
echo "🚀 DAILY COLLECTION STARTED at $(date)" | tee -a "$LOG_FILE"
echo "   Target date: $DATE" | tee -a "$LOG_FILE"
echo "   Leagues: ${LEAGUES[*]}" | tee -a "$LOG_FILE"
echo "   Season: $SEASON" | tee -a "$LOG_FILE"
echo "================================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# --- RUN FOR EACH LEAGUE ---
SUCCESS_COUNT=0
FAILURE_COUNT=0

for league in "${LEAGUES[@]}"; do
  echo "--- Processing League $league ---" | tee -a "$LOG_FILE"
  
  "$PY" "$SCRIPT_DIR/main.py" \
    --league "$league" \
    --season "$SEASON" \
    --date "$DATE" 2>&1 | tee -a "$LOG_FILE"

  EXIT_CODE=${PIPESTATUS[0]}

  if [ "$EXIT_CODE" -eq 0 ]; then
    echo "✅ League $league completed" | tee -a "$LOG_FILE"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))  
  else
    echo "❌ League $league failed" | tee -a "$LOG_FILE"
    FAILURE_COUNT=$((FAILURE_COUNT + 1))
  fi
  
  echo "" | tee -a "$LOG_FILE"
done

# --- SUMMARY ---
echo "================================================================================" | tee -a "$LOG_FILE"
echo "📊 Completed at $(date)" | tee -a "$LOG_FILE"
echo "   Successful: $SUCCESS_COUNT" | tee -a "$LOG_FILE"
echo "   Failed: $FAILURE_COUNT" | tee -a "$LOG_FILE"
echo "================================================================================" | tee -a "$LOG_FILE"

[ "$FAILURE_COUNT" -gt 0 ] && exit 1
echo "✅ All done!" | tee -a "$LOG_FILE"
