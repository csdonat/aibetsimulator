import json
from pathlib import Path
from utils.api import api_get
from utils.logger import get_logger

log = get_logger("LAST_MATCHES")

def collect_last_matches(teams, out_dir: Path, last: int = 10):
    """
    For each team in `teams` (list of team entries from teams.json),
    fetch the last `last` fixtures for that team and save as last_<teamid>.json
    under out_dir/last_matches/.
    """
    outdir = out_dir / "last_matches"
    outdir.mkdir(parents=True, exist_ok=True)

    total = len(teams)
    skipped = 0
    
    log.info(f"🚀 Collecting last {last} matches for {total} teams...")

    for idx, t in enumerate(teams, 1):
        team_id = t["team"]["id"]
        team_name = t["team"].get("name", team_id)
        out_file = outdir / f"last{last}_{team_id}.json"
        
        if out_file.exists():
            skipped += 1
            print(f"\r📥 Progress: {idx}/{total} ({idx*100//total}%) - ⏭️ Skipped: {team_name} (already exists)", end="", flush=True)
            continue

        data = api_get("fixtures", {"team": team_id, "last": last})
        if data is None:
            print(f"\r📥 Progress: {idx}/{total} ({idx*100//total}%) - ⚠️ No data: {team_name}", end="", flush=True)
            continue

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"\r📥 Progress: {idx}/{total} ({idx*100//total}%) - ✔ Latest: {team_name}", end="", flush=True)
    
    log.info(f"✔ Collection completed: {total - skipped} fetched, {skipped} skipped")