from pathlib import Path
from utils.api import api_get
import json
from utils.logger import get_logger

log = get_logger("H2H")

def collect_h2h(fixtures, out_dir: Path):
    """
    Collect H2H data for each unique pair of teams in the fixtures.
    Skips pairs that already have H2H data saved (efficient for daily updates).
    """
    seen_pairs = set()

    h2h_dir = out_dir / "h2h"
    h2h_dir.mkdir(exist_ok=True)

    # Collect unique pairs that need fetching
    pairs_to_fetch = []
    for fixture in fixtures:
        home_id = fixture["teams"]["home"]["id"]
        away_id = fixture["teams"]["away"]["id"]
        pair = tuple(sorted([home_id, away_id]))
        
        if pair not in seen_pairs:
            seen_pairs.add(pair)
            
            # Check if H2H data already exists
            h2h_file = h2h_dir / f"h2h_{pair[0]}_{pair[1]}.json"
            if not h2h_file.exists():
                pairs_to_fetch.append(pair)
    
    total = len(pairs_to_fetch)
    total_pairs = len(seen_pairs)
    
    if total == 0:
        log.info(f"ℹ️ All {total_pairs} team pairs already have H2H data")
        return

    log.info(f"🚀 Collecting H2H data for {total}/{total_pairs} new team pairs (skipping {total_pairs - total} existing)...")

    for idx, pair in enumerate(pairs_to_fetch, 1):
        # API call
        data = api_get("fixtures/headtohead", {"h2h": f"{pair[0]}-{pair[1]}"})

        if data:
            # Save full response
            out_file = h2h_dir / f"h2h_{pair[0]}_{pair[1]}.json"    
            with out_file.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"\r📥 Progress: {idx}/{total} ({idx*100//total}%) - ✔ Latest: {pair[0]} vs {pair[1]}", end="", flush=True)
        else:
            print(f"\r📥 Progress: {idx}/{total} ({idx*100//total}%) - ⚠️ Failed: {pair[0]} vs {pair[1]}", end="", flush=True)
    
    log.info(f"✔ H2H collection completed: {total} pairs saved")