import requests
import time
from config import API_KEY, BASE_URL

HEADERS = {
    "x-apisports-key": API_KEY
}

def api_get(endpoint: str, params: dict = None):
    """
    Makes a GET request to API-Football with rate limiting.
    Returns JSON dict or None.
    """
    url = f"{BASE_URL}/{endpoint}"

    try:
        response = requests.get(url, headers=HEADERS, params=params or {})
        response.raise_for_status()
        data = response.json()

        # API-level errors
        if data.get("errors"):
            print("API returned errors:", data["errors"])
            return None

        # Rate limiting: 250 req/min = 0.24s between requests
        time.sleep(0.25)
        
        return data

    except requests.RequestException as e:
        print("Request failed:", e)
        return None