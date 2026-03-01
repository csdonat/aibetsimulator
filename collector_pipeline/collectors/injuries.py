from pathlib import Path
from utils.api import api_get
import json
from utils.logger import get_logger

log = get_logger("INJURIES")

def collect_injuries(league_id: int, season: int, out_dir: Path):
    """
    Collect current injury reports for the season.
    Always fetches latest state and overwrites (injuries change daily).
    """
    log.info(f"🚀 Collecting current injuries for league={league_id}, season={season}")

    data = api_get("injuries", {
        "league": league_id,
        "season": season
    })

    out_file = out_dir / "injuries.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    log.info(f"✔ Injuries saved → {out_file}")