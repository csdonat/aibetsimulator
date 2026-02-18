from pathlib import Path
from utils.api import api_get
import json
from utils.logger import get_logger

log = get_logger("TEAMS")

def collect_teams(league_id: int, season: int, out_dir: Path):
    """Fetch all teams in the league for the season."""
    
    log.info(f"🚀 Collecting teams for league={league_id}, season={season}...")
    
    data = api_get("teams", {"league": league_id, "season": season})
    
    out_file = out_dir / "teams.json"

    with out_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    log.info(f"✔ Saved teams → {out_file}")
    
    return data.get("response", [])