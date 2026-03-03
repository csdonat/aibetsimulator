from pathlib import Path
import streamlit as st

BASE_DATA_DIR = Path("../data")

LEAGUE_MAP = {
    2: "UEFA Champions League",
    39: "Premier League (England)",
    140: "La Liga (Spain)",
    135: "Serie A (Italy)",
    78: "Bundesliga (Germany)",
    45: "FA Cup (England)",
    46: "EFL Cup (England)",
    61: "Legue 1 (France)",
    98: "Primeria Liga (Portugal)",
    143: "Copa Del Rey (Spain)",
    137: "Coppa Italia (Italy)",
    271: "NB I (Hungary)",
    556: "Super Cup (Spain)",
}

def select_league_season():
    league_ids = sorted(
        int(p.name)
        for p in BASE_DATA_DIR.iterdir()
        if p.is_dir() and p.name.isdigit()
    )

    league_options = {LEAGUE_MAP.get(lid, f"League {lid}"): lid for lid in league_ids}
    league_names = sorted(league_options.keys())

    # Persisted values (NOT widget keys)
    saved_league_id = st.session_state.get("league_id", league_ids[0])
    saved_league_name = LEAGUE_MAP.get(saved_league_id, f"League {saved_league_id}")
    league_index = league_names.index(saved_league_name) if saved_league_name in league_names else 0

    league_name = st.sidebar.selectbox(
        "Select League",
        league_names,
        index=league_index,
        key="league_select",   # widget key
    )
    league_id = league_options[league_name]

    # seasons for selected league
    season_dirs = sorted((BASE_DATA_DIR / str(league_id)).iterdir(), key=lambda x: x.name)
    season_names = [p.name for p in season_dirs if p.is_dir()]

    saved_season = str(st.session_state.get("season", season_names[-1]))
    season_index = season_names.index(saved_season) if saved_season in season_names else len(season_names) - 1

    season = st.sidebar.selectbox(
        "Select Season",
        season_names,
        index=season_index,
        key="season_select",   # widget key (different!)
    )

    # Store persisted values (safe, because different keys than widgets)
    st.session_state["league_id"] = int(league_id)
    st.session_state["season"] = int(season)

    data_dir = BASE_DATA_DIR / str(league_id) / str(season)
    return int(league_id), int(season), data_dir
