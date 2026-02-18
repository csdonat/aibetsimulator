from pathlib import Path
from utils.api import api_get
import json
from utils.logger import get_logger

log = get_logger("FIXTURES")

def collect_fixtures(season: int, league_id: int, out_dir: Path):
    """
    Download all fixtures of a league+season.
    """
    log.info(f"🚀 Collecting fixtures for season={season} league={league_id}...")

    data = api_get(
        "fixtures",
        {
            "league": league_id,
            "season": season
        }
    )

    # Save full response as fixtures.json
    out_file = out_dir / "fixtures.json"
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


    log.info(f"✔ Saved fixtures → {out_file}")
    return data.get("response", [])
