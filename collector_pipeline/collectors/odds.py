import json
from pathlib import Path
from utils.api import api_get
from datetime import datetime, timedelta, timezone
from utils.logger import get_logger

log = get_logger("ODDS")

def fetch_odds(fixtures, out_dir: Path):
    """
    Fetch/update odds for fixtures.
    Always updates odds even if file exists (odds change frequently).
    For daily runs: fetches only the provided fixtures.
    For full season: uses ±7 day window to avoid fetching old/far-future matches.
    """

    odds_dir = out_dir / "odds"
    odds_dir.mkdir(exist_ok=True)

    # If only a few fixtures (daily run), fetch all
    # If many fixtures (full season), use window filter
    if len(fixtures) <= 50:
        fixtures_to_fetch = fixtures
        log.info(f"🚀 Fetching odds for {len(fixtures_to_fetch)} fixtures (daily mode)...")
    else:
        today = datetime.now(timezone.utc)
        window_start = today - timedelta(days=7)
        window_end = today + timedelta(days=7)
        
        fixtures_to_fetch = []
        for fixture in fixtures:
            fixture_date = datetime.fromisoformat(fixture["fixture"]["date"])
            if window_start <= fixture_date <= window_end:
                fixtures_to_fetch.append(fixture)
        
        log.info(f"🚀 Fetching odds for {len(fixtures_to_fetch)}/{len(fixtures)} fixtures within ±7 day window...")
    
    total = len(fixtures_to_fetch)
    
    if total == 0:
        log.info("ℹ️ No fixtures to fetch odds for")
        return

    updated = 0
    failed = 0

    for idx, fixture in enumerate(fixtures_to_fetch, 1):
        fixture_id = fixture["fixture"]["id"]
        fixture_date = datetime.fromisoformat(fixture["fixture"]["date"])
        status = fixture["fixture"]["status"]["short"]

        data = api_get(
            "odds", {"fixture": fixture_id, "bookmaker": 16}  # Bookmaker 16 = Unibet
        )

        if data:
            out_path = odds_dir / f"odds_{fixture_id}.json"
            with out_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            updated += 1
            print(f"\r📥 Progress: {idx}/{total} ({idx*100//total}%) - ✔ Latest: fixture {fixture_id} ({fixture_date.date()}) [{status}]", end="", flush=True)
        else:
            failed += 1
            print(f"\r📥 Progress: {idx}/{total} ({idx*100//total}%) - ⚠️ Failed: fixture {fixture_id} ({fixture_date.date()}) [{status}]", end="", flush=True)
    
    print()  # New line after progress
    log.info(f"✔ Odds collection completed: {updated} updated, {failed} failed")