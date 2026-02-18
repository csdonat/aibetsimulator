from pathlib import Path
from utils.api import api_get
import json
from utils.logger import get_logger

log = get_logger("H2H")

def collect_h2h(fixtures, out_dir: Path):
    """
    Collect H2H data for each unique pair of teams in the fixtures.
    """
    seen_pairs = set()

    h2h_dir = out_dir / "h2h"
    h2h_dir.mkdir(exist_ok=True)

    # Collect unique pairs first
    unique_pairs = []
    for fixture in fixtures:
        home_id = fixture["teams"]["home"]["id"]
        away_id = fixture["teams"]["away"]["id"]
        pair = tuple(sorted([home_id, away_id]))
        if pair not in seen_pairs:
            seen_pairs.add(pair)
            unique_pairs.append(pair)
    
    total = len(unique_pairs)
    log.info(f"🚀 Collecting H2H data for {total} team pairs...")

    for idx, pair in enumerate(unique_pairs, 1):
        # API call
        data = api_get("fixtures/headtohead", {"h2h": f"{pair[0]}-{pair[1]}"})

        # Save full response
        out_file = h2h_dir / f"h2h_{pair[0]}_{pair[1]}.json"    
        with out_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        # Progress log (overwrites same line if possible)
        print(f"\r📥 Progress: {idx}/{total} ({idx*100//total}%) - Latest: {pair[0]} vs {pair[1]}", end="", flush=True)
    
    print()  # New line after progress
    log.info(f"✔ H2H collection completed: {total} pairs saved")