import streamlit as st
import pandas as pd
from pathlib import Path
from utils.selectors import select_league_season, LEAGUE_MAP
from utils.loader import load_json


st.set_page_config(layout="wide")

# -----------------------------
# UI
# -----------------------------
st.title("🏆 Standings")

league_id, season, data_dir = select_league_season()
st.write(f"### {LEAGUE_MAP.get(league_id)} — Season {season}")

standings_data = load_json(data_dir / "standings.json")
if not standings_data:
    st.error("No standings.json found for this league/season.")
    st.stop()

# -----------------------------
# Fancy display
# -----------------------------
league = standings_data["response"][0]["league"]
rows = league["standings"][0]

def form_chips(form: str) -> str:
    m = {"W": "🟩", "D": "🟨", "L": "🟥"}
    return " ".join(m.get(c, "⬜") for c in (form or "").strip())

# Header (logo + name)
h1, h2 = st.columns([1, 8])
with h1:
    st.image(league.get("logo"), width=64)
with h2:
    st.subheader(f"{league.get('name')} — {league.get('country')}")
    st.caption(f"League ID {league_id} • Season {season}")

# Metrics
leader = rows[0]["team"]["name"]
max_pts = max(r["points"] for r in rows)
best_gd = max(r["goalsDiff"] for r in rows)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Teams", len(rows))
c2.metric("Leader", leader)
c3.metric("Max points", max_pts)
c4.metric("Best GD", best_gd)

st.divider()

# Search
q = st.text_input("Search team", "")

# Card list
for r in rows:
    team = r["team"]
    name = team["name"]
    if q.strip() and q.strip().lower() not in name.lower():
        continue

    all_ = r["all"]
    gf = all_["goals"]["for"]
    ga = all_["goals"]["against"]
    desc = r.get("description") or "No qualifications"

    # color tag based on description
    border = "#333"
    if "Champions League" in desc:
        border = "#2e86de"
    elif "Europa League" in desc and "Conference" not in desc:
        border = "#f39c12"
    elif "Conference League" in desc:
        border = "#8e44ad"
    elif "Relegation" in desc:
        border = "#e74c3c"

    st.markdown(
        f"""
        <div style="
            border-left: 6px solid {border};
            padding: 10px 12px;
            margin: 8px 0;
            border-radius: 12px;
            background: rgba(255,255,255,0.03);
        ">
          <div style="display:flex; align-items:center; gap:12px;">
            <img src="{team.get('logo')}" style="width:28px; height:28px;" />
            <div style="flex:1;">
              <div style="font-weight:700; font-size:1.02rem;">
                {r["rank"]}. {name}
                <span style="opacity:0.7; font-weight:500;"> — {form_chips(r.get("form",""))}</span>
              </div>
              <div style="opacity:0.8; font-size:0.92rem;">
                <b>{r["points"]}</b> pts •
                P {all_["played"]} • W {all_["win"]} D {all_["draw"]} L {all_["lose"]} •
                GF {gf} GA {ga} • GD <b>{r["goalsDiff"]}</b>
              </div>
              {f"<div style='opacity:0.75; font-size:0.85rem; margin-top:3px;'><i>{desc}</i></div>"}
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )


