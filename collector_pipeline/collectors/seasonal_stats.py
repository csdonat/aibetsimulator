import json
from pathlib import Path
from utils.api import api_get
from utils.logger import get_logger

log = get_logger("SEASONAL_STATS")

def fetch_seasonal_stats(teams, league_id: int, season: int, out_dir: Path):
    """
    Download seasonal statistics for each team.
    """
    save_dir = out_dir / "team_stats"
    save_dir.mkdir(parents=True, exist_ok=True)

    total = len(teams)
    
    log.info(f"🚀 Fetching seasonal stats for {total} teams (league {league_id}, season {season})...")

    for idx, team in enumerate(teams, 1):
        team_id = team["team"]["id"]
        team_name = team["team"]["name"]

        data = api_get("teams/statistics", {"team": team_id, "league": league_id, "season": season})

        out_path = save_dir / f"team_{team_id}.json"

        with out_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        
        print(f"\r📥 Progress: {idx}/{total} ({idx*100//total}%) - ✔ Latest: {team_name}", end="", flush=True)

    log.info(f"✔ Seasonal stats collection completed: {total} teams processed")