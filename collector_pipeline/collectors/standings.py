from pathlib import Path
from utils.api import api_get
import json
from utils.logger import get_logger

log = get_logger("STANDINGS")

def fetch_standings(season: int, league_id: int, out_dir: Path):
    """
    Download all standings of a league+season.
    """
    log.info(f"🚀 Collecting standings for season={season} league={league_id}...")

    data = api_get(
        "standings",
        {
            "league": league_id,
            "season": season
        }
    )

    # Save full response as standings.json

    out_path = out_dir / "standings.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    log.info(f"✔ Saved standings → {out_path}")
    return data.get("response", [])
