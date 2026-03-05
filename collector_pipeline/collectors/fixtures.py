from pathlib import Path
from utils.api import api_get
import json
from utils.logger import get_logger

log = get_logger("FIXTURES")

def collect_fixtures(season: int, league_id: int, out_dir: Path, date: str = None, from_date: str = None, to_date: str = None):
    """
    Download all fixtures of a league+season, or for a specific date/date range.
    If date is provided (YYYY-MM-DD), fetches only that date and merges with existing.
    If from_date and to_date are provided, fetches date range and merges with existing.
    If none provided, fetches full season and overwrites.
    """
    if from_date and to_date:
        log.info(f"🚀 Collecting fixtures from {from_date} to {to_date} league={league_id} season={season}...")
        params = {
            "from": from_date,
            "to": to_date,
            "league": league_id,
            "season": season
        }
        merge_mode = True
    elif date:
        log.info(f"🚀 Collecting fixtures for date={date} league={league_id} season={season}...")
        params = {
            "date": date,
            "league": league_id,
            "season": season
        }
        merge_mode = True
    else:
        log.info(f"🚀 Collecting fixtures for season={season} league={league_id}...")
        params = {
            "league": league_id,
            "season": season
        }
        merge_mode = False

    data = api_get("fixtures", params)

    if not data:
        log.info(f"⚠️ No data returned")
        return []

    new_fixtures = data.get("response", [])
    out_file = out_dir / "fixtures.json"

    # If date/range filter: merge with existing fixtures
    if merge_mode and out_file.exists():
        date_info = f"{from_date} to {to_date}" if from_date and to_date else date
        log.info(f"📥 Found {len(new_fixtures)} fixtures for {date_info}, merging with existing...")
        try:
            with out_file.open("r", encoding="utf-8") as f:
                existing_data = json.load(f)
            
            # Create map of existing fixtures by ID
            existing_map = {}
            for fixture in existing_data.get("response", []):
                fixture_id = fixture.get("fixture", {}).get("id")
                if fixture_id:
                    existing_map[fixture_id] = fixture
            
            # Merge new fixtures
            updated, added = 0, 0
            for new_fixture in new_fixtures:
                fixture_id = new_fixture.get("fixture", {}).get("id")
                if fixture_id:
                    if fixture_id in existing_map:
                        existing_map[fixture_id] = new_fixture
                        updated += 1
                    else:
                        existing_map[fixture_id] = new_fixture
                        added += 1
            
            # Rebuild and sort
            merged_fixtures = list(existing_map.values())
            merged_fixtures.sort(key=lambda x: x.get("fixture", {}).get("date", ""))
            
            data["response"] = merged_fixtures
            data["results"] = len(merged_fixtures)
            
            log.info(f"   📊 Added: {added}, Updated: {updated}, Total: {len(merged_fixtures)}")
        except Exception as e:
            log.info(f"⚠️ Merge failed: {e}, saving new data only")

    # Save
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    log.info(f"✔ Saved fixtures → {out_file}")
    return new_fixtures if merge_mode else data.get("response", [])
