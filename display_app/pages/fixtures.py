import streamlit as st
import pandas as pd
from pathlib import Path
from utils.selectors import select_league_season, LEAGUE_MAP
from utils.loader import load_json


st.set_page_config(layout="wide")


def load_fixture_details(data_dir: Path, fixture_id: int):
    """Load all available fixture-related data."""
    return {
        "fixture": load_json(data_dir / "fixtures.json"),
        "stats": load_json(data_dir / "fixture_stats" / f"stats_{fixture_id}.json"),
        "lineup": load_json(data_dir / "lineups" / f"{fixture_id}.json"),
        "odds": load_json(data_dir / "odds" / f"odds_{fixture_id}.json"),
        "injuries": load_json(data_dir / "injuries.json"),  # filtered later
    }


def load_h2h(data_dir: Path, home_id, away_id):
    """Try both naming conventions."""
    h2h_path = data_dir / "h2h" / f"h2h_{home_id}_{away_id}.json"
    if h2h_path.exists():
        return load_json(h2h_path)

    h2h_path = data_dir / "h2h" / f"h2h_{away_id}_{home_id}.json"
    if h2h_path.exists():
        return load_json(h2h_path)

    return None


def load_last_matches(data_dir: Path, team_id: int):
    return load_json(data_dir / "last_matches" / f"last10_{team_id}.json")


def load_team_stats(data_dir: Path, team_id: int):
    return load_json(data_dir / "team_stats" / f"team_{team_id}.json")


# -----------------------------
# UI
# -----------------------------
st.title("📅 Fixtures")

league_id, season, data_dir = select_league_season()
st.write(f"### {LEAGUE_MAP.get(league_id)} — Season {season}")

fixtures_data = load_json(data_dir / "fixtures.json")
if len(fixtures_data.get("response", [])) == 0:
    st.warning("No fixtures found for this league/season.")
    st.stop()
if not fixtures_data:
    st.error("No fixtures.json found for this league/season.")
    st.stop()

# -----------------------------
# Build fixtures table
# -----------------------------
rows = []
for f in fixtures_data["response"]:
    fx = f["fixture"]
    tm = f["teams"]
    goals = f["goals"]

    rows.append({
        "Fixture ID": fx["id"],
        "Date": fx["date"][:10],
        "Time": fx["date"][11:16],
        "Home": tm["home"]["name"],
        "Away": tm["away"]["name"],
        "Score": f"{goals['home']} - {goals['away']}",
        "Home_ID": tm["home"]["id"],
        "Away_ID": tm["away"]["id"],
    })

df = pd.DataFrame(rows)

# Display interactive table
selected = st.dataframe(
    df.drop(columns=["Home_ID", "Away_ID"]),
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row",
    width='stretch',
)

# If no selection → stop
if not selected or "selection" not in selected or not selected["selection"]["rows"]:
    st.info("Click a fixture to display all available details.")
    st.stop()

row_idx = selected["selection"]["rows"][0]
fixture_row = df.iloc[row_idx]
fixture_id = int(fixture_row["Fixture ID"])
home_id = int(fixture_row["Home_ID"])
away_id = int(fixture_row["Away_ID"])

st.markdown("---")
st.subheader(f"🔍 Fixture Details — {fixture_row['Home']} vs {fixture_row['Away']} ({fixture_row['Date']})")

# -----------------------------
# Load all related data
# -----------------------------
details = load_fixture_details(data_dir, fixture_id)

# -----------------------------
# Display Stats
# -----------------------------
with st.expander("📊 Match Statistics", expanded=False):
    if details["stats"] and details["stats"]["response"]:
        for team_stats in details["stats"]["response"]:
            st.write(f"#### {team_stats['team']['name']}")
            st.dataframe(pd.DataFrame(team_stats["statistics"]), width='stretch')
    else:
        st.info("No stats available for this fixture.")

# -----------------------------
# Display Lineups
# -----------------------------
with st.expander("🧍 Lineups", expanded=False):
    if details["lineup"] and details["lineup"]["response"]:
        for lineup in details["lineup"]["response"]:
            st.write(f"#### {lineup['team']['name']} — Formation: {lineup['formation']}")
            starters = [p["player"]["name"] for p in lineup["startXI"]]
            subs = [p["player"]["name"] for p in lineup["substitutes"]]

            st.write("**Starting XI:**")
            st.write(", ".join(starters))
            st.write("**Substitutes:**")
            st.write(", ".join(subs))
    else:
        st.info("No lineup data.")

# -----------------------------
# Display Odds
# -----------------------------
with st.expander("💸 Betting Odds", expanded=False):
    odds = details["odds"]

    if not odds or not odds.get("response"):
        st.info("No odds available for this fixture.")
    else:
        r = odds["response"][0]
        bookmakers = r.get("bookmakers", [])

        if not bookmakers:
            st.info("No bookmakers in odds response.")
        else:
            # --- Bookmaker selector (even if only 1, it's fine)
            bm_map = {f"{b['name']} (id={b['id']})": b for b in bookmakers}
            selected_bm_label = st.selectbox("Bookmaker", list(bm_map.keys()))
            bm = bm_map[selected_bm_label]

            # --- Flatten into rows
            rows = []
            for bet in bm.get("bets", []):
                bet_name = bet.get("name", "")
                bet_id = bet.get("id", "")
                for v in bet.get("values", []):
                    rows.append({
                        "Market": bet_name,
                        "Selection": v.get("value", ""),
                        "Odd": float(v["odd"]) if v.get("odd") not in (None, "") else None,
                        "Market ID": bet_id,
                    })

            df_odds = pd.DataFrame(rows)

            if df_odds.empty:
                st.info("No bet markets found for this bookmaker.")
            else:
                # --- Optional: quick filter for popular markets
                popular_markets = [
                    "Match Winner",
                    "Double Chance",
                    "Both Teams Score",
                    "Goals Over/Under",
                    "Goals Over/Under First Half",
                    "Goals Over/Under - Second Half",
                    "Asian Handicap",
                    "Handicap Result",
                ]

                show_popular_only = st.checkbox("Show only popular markets", value=True)

                if show_popular_only:
                    df_view = df_odds[df_odds["Market"].isin(popular_markets)].copy()
                    if df_view.empty:
                        st.warning("No popular markets found — showing everything.")
                        df_view = df_odds.copy()
                else:
                    df_view = df_odds.copy()

                # Sort nicely
                df_view = df_view.sort_values(["Market", "Selection"])

                # --- Display as table
                st.dataframe(
                    df_view.drop(columns=["Market ID"]),
                    use_container_width=True,
                    hide_index=True,
                )

                # --- Bonus: grouped view per market (more “bookie-like”)
                st.write("### Markets (grouped)")
                for market, group in df_view.groupby("Market"):
                    st.write(f"**{market}**")
                    st.table(group[["Selection", "Odd"]].reset_index(drop=True))


# -----------------------------
# Display H2H
# -----------------------------
with st.expander("⚔️ Head-to-Head", expanded=False):
    h2h = load_h2h(data_dir, home_id, away_id)
    if h2h:
        rows = []
        for m in h2h["response"]:
            fx = m["fixture"]
            tm = m["teams"]
            gl = m["goals"]
            rows.append({
                "Date": fx["date"][:10],
                "Home": tm["home"]["name"],
                "Away": tm["away"]["name"],
                "Score": f"{gl['home']} - {gl['away']}",
            })
        st.dataframe(pd.DataFrame(rows), width='stretch')
    else:
        st.info("No H2H data found.")

# -----------------------------
# Display Last Matches
# -----------------------------
with st.expander("📈 Last 10 Matches — Form", expanded=False):
    col1, col2 = st.columns(2)

    def _last_matches_df(last_json: dict) -> pd.DataFrame:
        if not last_json or not last_json.get("response"):
            return pd.DataFrame()

        rows = []
        for item in last_json["response"]:
            fx = item.get("fixture", {})
            league = item.get("league", {})
            teams = item.get("teams", {})
            goals = item.get("goals", {})
            score = item.get("score", {})
            venue = fx.get("venue", {})
            status = fx.get("status", {})

            rows.append({
                "Date": fx.get("date", "")[:10],
                "Time": fx.get("date", "")[11:16],
                "Competition": league.get("name"),
                "Round": league.get("round"),
                "Home": teams.get("home", {}).get("name"),
                "Away": teams.get("away", {}).get("name"),
                "FT": f"{goals.get('home')} - {goals.get('away')}",
                "HT": f"{score.get('halftime', {}).get('home')} - {score.get('halftime', {}).get('away')}",
                "Status": status.get("short"),
                "Venue": venue.get("name"),
                "City": venue.get("city"),
                "Fixture ID": fx.get("id"),
            })

        dfm = pd.DataFrame(rows)
        if not dfm.empty:
            dfm = dfm.sort_values(["Date", "Time"], ascending=False, ignore_index=True)
        return dfm

    with col1:
        st.subheader(f"{fixture_row['Home']} — Last 10")
        home_last = load_last_matches(data_dir, home_id)
        df_home = _last_matches_df(home_last)

        if df_home.empty:
            st.info("No last matches data.")
        else:
            st.dataframe(
                df_home.drop(columns=["Fixture ID"]),
                use_container_width=True,
                hide_index=True
            )

    with col2:
        st.subheader(f"{fixture_row['Away']} — Last 10")
        away_last = load_last_matches(data_dir, away_id)
        df_away = _last_matches_df(away_last)

        if df_away.empty:
            st.info("No last matches data.")
        else:
            st.dataframe(
                df_away.drop(columns=["Fixture ID"]),
                use_container_width=True,
                hide_index=True
            )


# -----------------------------
# Team Seasonal Stats
# -----------------------------
with st.expander("📘 Seasonal Team Stats", expanded=False):
    col1, col2 = st.columns(2)

    def _render_team_stats(team_name: str, team_stats_json: dict):
        if not team_stats_json or not team_stats_json.get("response"):
            st.info("No team stats found.")
            return

        r = team_stats_json["response"]

        # ----------------- Top metrics -----------------
        fixtures = r.get("fixtures", {})
        goals = r.get("goals", {})
        cs = r.get("clean_sheet", {})
        fts = r.get("failed_to_score", {})

        played_total = fixtures.get("played", {}).get("total", 0)
        wins_total = fixtures.get("wins", {}).get("total", 0)
        draws_total = fixtures.get("draws", {}).get("total", 0)
        loses_total = fixtures.get("loses", {}).get("total", 0)

        gf_total = goals.get("for", {}).get("total", {}).get("total", 0)
        ga_total = goals.get("against", {}).get("total", {}).get("total", 0)

        avg_gf = goals.get("for", {}).get("average", {}).get("total", None)
        avg_ga = goals.get("against", {}).get("average", {}).get("total", None)

        clean_sheets = r.get("clean_sheet", {}).get("total", 0)
        failed_score = r.get("failed_to_score", {}).get("total", 0)

        st.markdown("#### Key Summary")
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("Played", played_total)
        m2.metric("W", wins_total)
        m3.metric("D", draws_total)
        m4.metric("L", loses_total)
        m5.metric("GF / GA", f"{gf_total} / {ga_total}")
        m6.metric("CS / FTS", f"{clean_sheets} / {failed_score}")

        # ----------------- Goals (totals + averages) -----------------
        st.markdown("#### Goals Summary")
        goals_rows = []
        for side in ["home", "away", "total"]:
            goals_rows.append({
                "Side": side.title(),
                "GF": goals.get("for", {}).get("total", {}).get(side, None),
                "GA": goals.get("against", {}).get("total", {}).get(side, None),
                "Avg GF": goals.get("for", {}).get("average", {}).get(side, None),
                "Avg GA": goals.get("against", {}).get("average", {}).get(side, None),
            })
        st.dataframe(pd.DataFrame(goals_rows), use_container_width=True, hide_index=True)

        # ----------------- Form string -----------------
        form = r.get("form")
        if form:
            st.markdown(f"#### Form (latest → oldest)\n`{form}`")

        # ----------------- Goals by minute (FOR + AGAINST) -----------------
        st.markdown("#### Goals by Minute")
        gf_min = goals.get("for", {}).get("minute", {}) or {}
        ga_min = goals.get("against", {}).get("minute", {}) or {}

        minute_rows = []
        for bucket in ["0-15", "16-30", "31-45", "46-60", "61-75", "76-90", "91-105", "106-120"]:
            gf_bucket = gf_min.get(bucket, {}) or {}
            ga_bucket = ga_min.get(bucket, {}) or {}
            minute_rows.append({
                "Minute": bucket,
                "GF": gf_bucket.get("total"),
                "GF %": gf_bucket.get("percentage"),
                "GA": ga_bucket.get("total"),
                "GA %": ga_bucket.get("percentage"),
            })
        st.dataframe(pd.DataFrame(minute_rows), use_container_width=True, hide_index=True)

        # ----------------- Over/Under (team goals for + against) -----------------
        st.markdown("#### Over / Under (Matches)")
        ou_for = goals.get("for", {}).get("under_over", {}) or {}
        ou_against = goals.get("against", {}).get("under_over", {}) or {}

        ou_rows = []
        # keys look like "0.5", "1.5", ...
        all_lines = sorted(set(list(ou_for.keys()) + list(ou_against.keys())), key=lambda x: float(x))
        for line in all_lines:
            ou_rows.append({
                "Line": line,
                "GF Over": ou_for.get(line, {}).get("over"),
                "GF Under": ou_for.get(line, {}).get("under"),
                "GA Over": ou_against.get(line, {}).get("over"),
                "GA Under": ou_against.get(line, {}).get("under"),
            })
        st.dataframe(pd.DataFrame(ou_rows), use_container_width=True, hide_index=True)

        # ----------------- Lineups used -----------------
        st.markdown("#### Formations Used")
        lineups = r.get("lineups", []) or []
        if lineups:
            df_lineups = pd.DataFrame([{
                "Formation": x.get("formation"),
                "Played": x.get("played"),
            } for x in lineups]).sort_values("Played", ascending=False)
            st.dataframe(df_lineups, use_container_width=True, hide_index=True)
        else:
            st.info("No formation data available.")

        # ----------------- Cards by minute -----------------
        st.markdown("#### Cards by Minute")
        cards = r.get("cards", {}) or {}
        yellow = cards.get("yellow", {}) or {}
        red = cards.get("red", {}) or {}

        card_rows = []
        for bucket in ["0-15", "16-30", "31-45", "46-60", "61-75", "76-90", "91-105", "106-120"]:
            yb = yellow.get(bucket, {}) or {}
            rb = red.get(bucket, {}) or {}
            card_rows.append({
                "Minute": bucket,
                "Yellow": yb.get("total"),
                "Yellow %": yb.get("percentage"),
                "Red": rb.get("total"),
                "Red %": rb.get("percentage"),
            })
        st.dataframe(pd.DataFrame(card_rows), use_container_width=True, hide_index=True)

        # ----------------- Biggest streaks / results -----------------
        st.markdown("#### Biggest (Streaks / Extremes)")
        biggest = r.get("biggest", {}) or {}
        streak = biggest.get("streak", {}) or {}
        biggest_rows = [
            {"Metric": "Win streak", "Value": streak.get("wins")},
            {"Metric": "Draw streak", "Value": streak.get("draws")},
            {"Metric": "Lose streak", "Value": streak.get("loses")},
            {"Metric": "Biggest win (home)", "Value": biggest.get("wins", {}).get("home")},
            {"Metric": "Biggest win (away)", "Value": biggest.get("wins", {}).get("away")},
            {"Metric": "Biggest loss (home)", "Value": biggest.get("loses", {}).get("home")},
            {"Metric": "Biggest loss (away)", "Value": biggest.get("loses", {}).get("away")},
        ]
        st.dataframe(pd.DataFrame(biggest_rows), use_container_width=True, hide_index=True)

    # ---- left team ----
    with col1:
        st.subheader(fixture_row["Home"])
        _render_team_stats(fixture_row["Home"], load_team_stats(data_dir, home_id))

    # ---- right team ----
    with col2:
        st.subheader(fixture_row["Away"])
        _render_team_stats(fixture_row["Away"], load_team_stats(data_dir, away_id))

# -----------------------------
# Display Injuries (for this fixture)
# -----------------------------
with st.expander("🚑 Injuries (Fixture)", expanded=False):
    injuries = details.get("injuries")

    if not injuries or not injuries.get("response"):
        st.info("No injuries data.")
    else:
        inj_rows = []

        for item in injuries["response"]:
            fx = item.get("fixture") or {}
            team = item.get("team") or {}
            player = item.get("player") or {}

            # Primary: match by fixture id if present
            if fx.get("id") is not None:
                if int(fx["id"]) != fixture_id:
                    continue
            else:
                # Fallback: if no fixture in injury item, keep only teams in this match
                tid = team.get("id")
                if tid not in (home_id, away_id):
                    continue

            inj_rows.append({
                "Team": team.get("name"),
                "Player": player.get("name"),
                "Type": player.get("type"),
                "Reason": player.get("reason"),
                "Since": player.get("since"),
                "Fixture date": fx.get("date", "")[:10] if fx.get("date") else None,
            })

        if not inj_rows:
            st.info("No injuries found for this fixture.")
        else:
            df_inj = pd.DataFrame(inj_rows)

            # Make it look nice: group by team
            col1, col2 = st.columns(2)

            with col1:
                st.subheader(f"🚑 {fixture_row['Home']}")
                home_df = df_inj[df_inj["Team"] == fixture_row["Home"]].drop(columns=["Team"])
                if home_df.empty:
                    st.caption("No injuries listed.")
                else:
                    st.dataframe(home_df, use_container_width=True, hide_index=True)

            with col2:
                st.subheader(f"🚑 {fixture_row['Away']}")
                away_df = df_inj[df_inj["Team"] == fixture_row["Away"]].drop(columns=["Team"])
                if away_df.empty:
                    st.caption("No injuries listed.")
                else:
                    st.dataframe(away_df, use_container_width=True, hide_index=True)

            # Optional: show combined table
            with st.expander("Show combined injuries table", expanded=False):
                st.dataframe(df_inj, use_container_width=True, hide_index=True)
