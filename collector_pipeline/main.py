# Central script to execute all collectors in order.

import argparse
from pathlib import Path
from config import get_data_dir
from collectors.fixtures import collect_fixtures
from collectors.teams import collect_teams
from collectors.players import collect_players
from collectors.stats import collect_fixture_stats
from collectors.h2h import collect_h2h
from collectors.injuries import collect_injuries
from collectors.last_matches import collect_last_matches
from collectors.lineups import fetch_lineups
from collectors.seasonal_stats import fetch_seasonal_stats
from collectors.odds import fetch_odds
from collectors.standings import fetch_standings
import time
from utils.timer import timed
from utils.logger import get_logger

log = get_logger("MAIN")

def main():
    start_time = time.time()  # ⏱ Start timing


    parser = argparse.ArgumentParser(description="Collector Pipeline")
    parser.add_argument("--season", type=int, required=True, help="Season year, e.g. 2022")
    parser.add_argument("--league", type=int, default=39, help="League ID (default 39 = Premier League)")
    parser.add_argument("--date", type=str, help="Specific date to collect (YYYY-MM-DD). If not provided, collects full season.")

    args = parser.parse_args()

    output_dir = get_data_dir(args.league, args.season)
    log.info(f"Saving dataset to: {output_dir}")
    if args.date:
        log.info(f"Date filter: {args.date}")

    # --- Collectors with timing---
    # --- Standings ---
    standings = timed(
        "Standings", 
        fetch_standings, args.season, args.league, output_dir
    )

    # --- Fixtures ---
    fixtures = timed(
        "Fixtures", 
        collect_fixtures, args.season, args.league, output_dir, args.date
    )

    timed("Fixture Stats", collect_fixture_stats, fixtures, output_dir)
    timed("H2H", collect_h2h, fixtures, output_dir)
    timed("Lineups", fetch_lineups, fixtures, output_dir)

    # --- Odds ---
    timed("Odds", fetch_odds, fixtures, output_dir)
    
    # --- Injuries ---
    timed("Injuries", collect_injuries, args.league, args.season, output_dir)

    # --- Teams ---
    teams = timed("Teams", collect_teams, args.league, args.season, output_dir)
    timed("Last Matches", collect_last_matches, teams, output_dir, 10)
    timed("Players", collect_players, teams, args.season, output_dir)
    timed("Seasonal Stats", fetch_seasonal_stats, teams, args.league, args.season, output_dir)

    total_seconds = round(time.time() - start_time, 2)
    log.info(f"🎉 All collectors finished in {total_seconds} seconds.")

if __name__ == "__main__":
    main()
