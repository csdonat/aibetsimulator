# fixture stats
from pathlib import Path
from utils.api import api_get
import json
from utils.logger import get_logger

log = get_logger("FIXTURE_STATS")

def collect_fixture_stats(fixtures, out_dir: Path):
    """
    Download fixture stats only for completed matches that don't have stats yet.
    This makes it efficient for daily updates.
    """

    stats_dir = out_dir / "fixture_stats"
    stats_dir.mkdir(exist_ok=True)
    
    # Filter for finished matches without existing stats
    fixtures_to_fetch = []
    for fixture in fixtures:
        fixture_id = fixture["fixture"]["id"]
        status = fixture["fixture"]["status"]["short"]
        
        # Only fetch if match is finished and stats don't exist
        stats_file = stats_dir / f"stats_{fixture_id}.json"
        if status in ["FT", "AET", "PEN"] and not stats_file.exists():
            fixtures_to_fetch.append(fixture)
    
    total = len(fixtures_to_fetch)
    
    if total == 0:
        log.info("ℹ️ No new completed matches requiring stats collection")
        return
    
    log.info(f"🚀 Collecting stats for {total} completed fixtures (skipping {len(fixtures) - total} existing/unfinished)...")

    for idx, fixture in enumerate(fixtures_to_fetch, 1):
        fixture_id = fixture["fixture"]["id"]
        home_team = fixture['teams']['home']['name']
        away_team = fixture['teams']['away']['name']

        data = api_get(
            "fixtures/statistics",
            {
                "fixture": fixture_id
            }
        )

        if data:
            out_file = stats_dir / f"stats_{fixture_id}.json"
            with out_file.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            
            print(f"\r📥 Progress: {idx}/{total} ({idx*100//total}%) - ✔ Latest: {home_team} vs {away_team}", end="", flush=True)
        else:
            print(f"\r📥 Progress: {idx}/{total} ({idx*100//total}%) - ⚠️ Failed: {home_team} vs {away_team}", end="", flush=True)

    log.info(f"✔ Fixture stats collection completed: {total} fixtures processed")