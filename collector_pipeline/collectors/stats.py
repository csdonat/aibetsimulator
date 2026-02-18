# fixture stats
from pathlib import Path
from utils.api import api_get
import json
from utils.logger import get_logger

log = get_logger("FIXTURE_STATS")

def collect_fixture_stats(fixtures, out_dir: Path):
    """
    Download all fixture stats.
    """

    stats_dir = out_dir / "fixture_stats"
    stats_dir.mkdir(exist_ok=True)
    
    total = len(fixtures)
    
    log.info(f"🚀 Collecting stats for {total} fixtures...")

    for idx, fixture in enumerate(fixtures, 1):
        fixture_id = fixture["fixture"]["id"]
        home_team = fixture['teams']['home']['name']
        away_team = fixture['teams']['away']['name']

        data = api_get(
            "fixtures/statistics",
            {
                "fixture": fixture_id
            }
        )

        # Save full response as players.json
        out_file = stats_dir / f"stats_{fixture_id}.json"
        with out_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        
        print(f"\r📥 Progress: {idx}/{total} ({idx*100//total}%) - ✔ Latest: {home_team} vs {away_team}", end="", flush=True)

    print()  # New line after progress
    log.info(f"✔ Fixture stats collection completed: {total} fixtures processed")