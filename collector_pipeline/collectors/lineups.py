from pathlib import Path
from utils.api import api_get
import json
from utils.logger import get_logger

log = get_logger("LINEUPS")

def fetch_lineups(fixtures, out_dir: Path):
    """
    Fetch lineups for fixtures. Skips fixtures that already have lineups saved.
    Efficient for daily updates - only fetches new matches.
    """
    lineups_dir = out_dir / "lineups"
    lineups_dir.mkdir(exist_ok=True)

    total = len(fixtures)
    
    if total == 0:
        log.info("ℹ️ No fixtures to fetch lineups for")
        return
    
    skipped = 0
    
    log.info(f"🚀 Collecting lineups for {total} fixtures...")

    for idx, fixture in enumerate(fixtures, 1):
        fixture_id = fixture["fixture"]["id"]
        out_file = lineups_dir / f"{fixture_id}.json"
        
        if out_file.exists():
            skipped += 1
            print(f"\r📥 Progress: {idx}/{total} ({idx*100//total}%) - ⏭️ Skipped: fixture {fixture_id} (already exists)", end="", flush=True)
            continue

        data = api_get("fixtures/lineups", {"fixture": fixture_id})

        if data:
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\r📥 Progress: {idx}/{total} ({idx*100//total}%) - ✔ Latest: fixture {fixture_id}", end="", flush=True)
        else:
            print(f"\r📥 Progress: {idx}/{total} ({idx*100//total}%) - ⚠️ Failed: fixture {fixture_id}", end="", flush=True)
    
    print()  # New line after progress
    
    if total - skipped == 0:
        log.info(f"ℹ️ All {total} lineups already exist, nothing new to fetch")
    else:
        log.info(f"✔ Lineups collection completed: {total - skipped} fetched, {skipped} skipped")