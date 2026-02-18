import json
from pathlib import Path
from utils.api import api_get
from datetime import datetime, timedelta, timezone
from utils.logger import get_logger

log = get_logger("ODDS")

def fetch_odds(fixtures, out_dir: Path):
    """
    Fetch odds ONLY for fixtures in a +-7 day window.
    fixtures: list of fixture objects from the API
    """

    today = datetime.now(timezone.utc)
    window_start = today - timedelta(days=7)
    window_end = today + timedelta(days=7)

    odds_dir = out_dir / "odds"
    odds_dir.mkdir(exist_ok=True)

    # Filter fixtures within window
    fixtures_in_window = []
    for fixture in fixtures:
        fixture_date = datetime.fromisoformat(fixture["fixture"]["date"])
        if window_start <= fixture_date <= window_end:
            fixtures_in_window.append(fixture)
    
    total = len(fixtures_in_window)
    total_fixtures = len(fixtures)
    
    log.info(f"🚀 Fetching odds for {total}/{total_fixtures} fixtures within ±7 day window...")

    for idx, fixture in enumerate(fixtures_in_window, 1):
        fixture_id = fixture["fixture"]["id"]
        fixture_date = datetime.fromisoformat(fixture["fixture"]["date"])

        data = api_get(
            "odds", {"fixture": fixture_id, "bookmaker": 16}  # Bookmaker 16 = Unibet
        )

        out_path = odds_dir / f"odds_{fixture_id}.json"
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"\r📥 Progress: {idx}/{total} ({idx*100//total}%) - ✔ Latest: fixture {fixture_id} ({fixture_date.date()})", end="", flush=True)
    
    print()  # New line after progress
    log.info(f"✔ Odds collection completed: {total} fixtures fetched")