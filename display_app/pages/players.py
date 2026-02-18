import streamlit as st
import pandas as pd
from pathlib import Path

from utils.selectors import select_league_season, LEAGUE_MAP
from utils.loader import load_json

st.set_page_config(layout="wide")
st.title("🧑‍🤝‍🧑 Players (All Teams)")

league_id, season, data_dir = select_league_season()
league_name = LEAGUE_MAP.get(league_id, f"League {league_id}")
st.write(f"### {league_name} — Season {season}")

players_dir = data_dir / "players"
if not players_dir.exists():
    st.error("No players/ directory found for this league/season.")
    st.stop()

# ---------------------------------
# Helpers
# ---------------------------------
def pick_main_stats(stats_list: list, league_id: int):
    if not stats_list:
        return None
    for s in stats_list:
        if (s.get("league") or {}).get("id") == league_id:
            return s
    return stats_list[0]

def build_players_df(players_json: dict) -> pd.DataFrame:
    resp = players_json.get("response") or []
    rows = []
    for item in resp:
        p = item.get("player") or {}
        stats_list = item.get("statistics") or []

        main = pick_main_stats(stats_list, league_id)
        games = (main or {}).get("games") or {}
        goals = (main or {}).get("goals") or {}
        cards = (main or {}).get("cards") or {}

        rows.append({
            "Player ID": p.get("id"),
            "Name": p.get("name"),
            "Age": p.get("age"),
            "Nationality": p.get("nationality"),
            "Position": games.get("position"),
            "Number": games.get("number"),
            "Apps": games.get("appearences"),
            "Minutes": games.get("minutes"),
            "Goals": goals.get("total"),
            "Assists": goals.get("assists"),
            "Yellow": cards.get("yellow"),
            "Red": cards.get("red"),
            "Rating": float(games["rating"]) if games.get("rating") not in (None, "") else None,
            "_photo": p.get("photo"),
            "_stats": stats_list,
            "_raw": item,
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(["Minutes", "Apps"], ascending=False, na_position="last").reset_index(drop=True)
    return df

def _to_int(x, default=0):
    try:
        if x is None or x == "":
            return default
        return int(float(x))
    except Exception:
        return default

def render_player_details(player_row: pd.Series):
    st.markdown("---")

    stats_list = player_row.get("_stats") or []
    if not stats_list:
        st.info("No stats available for this player.")
        return

    # ---------------- Header card ----------------
    col_img, col_main = st.columns([1, 4])

    with col_img:
        if player_row.get("_photo"):
            st.image(player_row["_photo"], width=150)

    with col_main:
        st.subheader(player_row["Name"])

        meta = []
        if pd.notna(player_row.get("Age")):
            meta.append(f"Age **{int(player_row['Age'])}**")
        if player_row.get("Nationality"):
            meta.append(player_row["Nationality"])
        if player_row.get("Position"):
            meta.append(player_row["Position"])
        if pd.notna(player_row.get("Number")):
            meta.append(f"#{int(player_row['Number'])}")
        st.write(" • ".join(meta))

        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("Apps", _to_int(player_row.get("Apps"), 0))
        m2.metric("Minutes", _to_int(player_row.get("Minutes"), 0))
        m3.metric("Goals", _to_int(player_row.get("Goals"), 0))
        m4.metric("Assists", _to_int(player_row.get("Assists"), 0))
        m5.metric("Yellow", _to_int(player_row.get("Yellow"), 0))
        rating = player_row.get("Rating")
        m6.metric("Rating", f"{rating:.2f}" if pd.notna(rating) else "—")

    # ---------------- Competition breakdown (overview) ----------------
    with st.expander("📊 Competition breakdown (overview)", expanded=True):
        rows = []
        for s in stats_list:
            league = s.get("league") or {}
            games = s.get("games") or {}
            goals = s.get("goals") or {}
            shots = s.get("shots") or {}
            passes = s.get("passes") or {}
            tackles = s.get("tackles") or {}
            duels = s.get("duels") or {}
            cards = s.get("cards") or {}

            rows.append({
                "Competition": league.get("name"),
                "Apps": games.get("appearences"),
                "Lineups": games.get("lineups"),
                "Minutes": games.get("minutes"),
                "Position": games.get("position"),
                "Goals": goals.get("total"),
                "Assists": goals.get("assists"),
                "Shots": shots.get("total"),
                "On target": shots.get("on"),
                "Key passes": passes.get("key"),
                "Tackles": tackles.get("total"),
                "Duels won": duels.get("won"),
                "Yellow": cards.get("yellow"),
                "Red": cards.get("red"),
                "Rating": games.get("rating"),
            })

        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ---------------- Shots & Goals ----------------
    with st.expander("🎯 Attacking (shots & goals)", expanded=False):
        rows = []
        for s in stats_list:
            league = s.get("league") or {}
            games = s.get("games") or {}
            shots = s.get("shots") or {}
            goals = s.get("goals") or {}
            pen = s.get("penalty") or {}

            rows.append({
                "Competition": league.get("name"),
                "Apps": games.get("appearences"),
                "Minutes": games.get("minutes"),
                "Shots": shots.get("total"),
                "On target": shots.get("on"),
                "Goals": goals.get("total"),
                "Assists": goals.get("assists"),
                "Pen scored": pen.get("scored"),
                "Pen missed": pen.get("missed"),
                "Pen won": pen.get("won"),
            })

        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ---------------- Passing ----------------
    with st.expander("🧠 Passing", expanded=False):
        rows = []
        for s in stats_list:
            league = s.get("league") or {}
            games = s.get("games") or {}
            passes = s.get("passes") or {}

            rows.append({
                "Competition": league.get("name"),
                "Apps": games.get("appearences"),
                "Minutes": games.get("minutes"),
                "Passes": passes.get("total"),
                "Key passes": passes.get("key"),
                "Accuracy": passes.get("accuracy"),  # sometimes None
            })

        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ---------------- Defending ----------------
    with st.expander("🛡️ Defending (tackles & blocks)", expanded=False):
        rows = []
        for s in stats_list:
            league = s.get("league") or {}
            games = s.get("games") or {}
            tackles = s.get("tackles") or {}

            rows.append({
                "Competition": league.get("name"),
                "Apps": games.get("appearences"),
                "Minutes": games.get("minutes"),
                "Tackles": tackles.get("total"),
                "Blocks": tackles.get("blocks"),
                "Interceptions": tackles.get("interceptions"),
            })

        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ---------------- Dribbling ----------------
    with st.expander("🌀 Dribbling", expanded=False):
        rows = []
        for s in stats_list:
            league = s.get("league") or {}
            games = s.get("games") or {}
            dr = s.get("dribbles") or {}

            rows.append({
                "Competition": league.get("name"),
                "Apps": games.get("appearences"),
                "Minutes": games.get("minutes"),
                "Attempts": dr.get("attempts"),
                "Success": dr.get("success"),
                "Past": dr.get("past"),
            })

        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ---------------- Duels & Discipline ----------------
    with st.expander("💥 Duels & discipline", expanded=False):
        rows = []
        for s in stats_list:
            league = s.get("league") or {}
            games = s.get("games") or {}
            duels = s.get("duels") or {}
            fouls = s.get("fouls") or {}
            cards = s.get("cards") or {}

            rows.append({
                "Competition": league.get("name"),
                "Apps": games.get("appearences"),
                "Minutes": games.get("minutes"),
                "Duels": duels.get("total"),
                "Duels won": duels.get("won"),
                "Fouls committed": fouls.get("committed"),
                "Fouls drawn": fouls.get("drawn"),
                "Yellow": cards.get("yellow"),
                "Red": cards.get("red"),
            })

        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ---------------- Goalkeeper-only section ----------------
    # If a player has saves/conceded in any competition, show GK expander.
    gk_rows = []
    for s in stats_list:
        goals = s.get("goals") or {}
        if goals.get("saves") is not None or goals.get("conceded") is not None:
            league = s.get("league") or {}
            games = s.get("games") or {}
            gk_rows.append({
                "Competition": league.get("name"),
                "Apps": games.get("appearences"),
                "Minutes": games.get("minutes"),
                "Conceded": goals.get("conceded"),
                "Saves": goals.get("saves"),
            })

    if gk_rows:
        with st.expander("🧤 Goalkeeping", expanded=False):
            st.dataframe(pd.DataFrame(gk_rows), use_container_width=True, hide_index=True)



# ---------------------------------
# Find team files
# ---------------------------------
team_files = sorted(players_dir.glob("players_team_*.json"))
if not team_files:
    st.error("No players_team_*.json files found in players/.")
    st.stop()

# Build teams list (id + name) with minimal reads
teams = []
for fp in team_files:
    try:
        team_id = int(fp.stem.split("_")[-1])
    except Exception:
        continue

    data = load_json(fp)
    if not data or not data.get("response"):
        continue

    # Try to get team name from first player's statistics
    team_name = f"Team {team_id}"
    first = data["response"][0]
    stats0 = (first.get("statistics") or [{}])[0]
    team_name = (stats0.get("team") or {}).get("name") or team_name

    teams.append((team_id, team_name, fp))

if not teams:
    st.error("Found files, but couldn't load any team data.")
    st.stop()

teams = sorted(teams, key=lambda x: x[1])  # sort by name

# ---------------------------------
# Global filters (apply inside each team)
# ---------------------------------

tab_labels = [name for _, name, _ in teams]
tabs = st.tabs(tab_labels)

for (team_id, team_name, fp), tab in zip(teams, tabs):
    with tab:
        team_json = load_json(fp)
        df = build_players_df(team_json)

        if df.empty:
            st.info("No players.")
            continue

        view = df.copy()

        c1, c2, c3 = st.columns([2, 1, 1])
        c1.write(f"#### {team_name} (id={team_id})")
        c2.metric("Players", len(view))
        c3.metric("Total players in file", len(df))

        selected = st.dataframe(
            view.drop(columns=["_photo", "_stats", "_raw"]),
            hide_index=True,
            selection_mode="single-row",
            on_select="rerun",
            use_container_width=True,
        )

        if selected and selected.get("selection") and selected["selection"]["rows"]:
            idx = selected["selection"]["rows"][0]
            player_row = view.iloc[idx]
            render_player_details(player_row)
        else:
            st.info("Click a player to see details.")
