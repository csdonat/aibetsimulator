# Stores API key, league, season, base URL, and output folder.
import os
from pathlib import Path

# Your API key
# API_KEY = os.getenv("API_FOOTBALL_KEY", "<PUT_YOUR_API_KEY_HERE>")
API_KEY = "d5b2f95e925d79bdd99fb123d4978632"

# Base URL for API-Football
BASE_URL = "https://v3.football.api-sports.io"

# Default league + season
LEAGUE_ID = 39        # Premier League
# SEASON = 2025         # You will make this dynamic later

# Output directory for collected data
DATA_DIR = Path("../data")

def get_data_dir(league_id: int, season: int) -> Path:
    """
    Return: data/<league_id>/<season>/
    and create the folder if missing.
    """
    path = DATA_DIR / str(league_id) / str(season)
    path.mkdir(parents=True, exist_ok=True)
    return path
