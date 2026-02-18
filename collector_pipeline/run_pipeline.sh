#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$SCRIPT_DIR/.venv/bin/python"

LEAGUES=(2)
SEASONS=(2025)

#"$PY" main.py --league 2 --season 2024

for league in "${LEAGUES[@]}"; do
  for season in "${SEASONS[@]}"; do
    echo "=== league=$league season=$season ==="
    "$PY" main.py --league "$league" --season "$season"
  done
done
echo "=== All done ==="
