from pathlib import Path
from utils.api import api_get
import json
from utils.logger import get_logger

log = get_logger("PLAYERS")

def collect_players(teams, season: int, out_dir: Path):
    """
    Download all players of a league+season.
    """
    players_dir = out_dir / "players"
    players_dir.mkdir(exist_ok=True)

    total = len(teams)
    
    log.info(f"🚀 Collecting players for {total} teams (season {season})...")

    for idx, team in enumerate(teams, 1):
        team_id = team["team"]["id"]
        team_name = team["team"]["name"]

        data = api_get(
            "players",
            {
                "team": team_id,
                "season": season
            }
        )

        # Save full response as players.json
        out_file = players_dir / f"players_team_{team_id}.json"
        with out_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        
        print(f"\r📥 Progress: {idx}/{total} ({idx*100//total}%) - ✔ Latest: {team_name}", end="", flush=True)

    log.info(f"✔ Players collection completed: {total} teams processed")