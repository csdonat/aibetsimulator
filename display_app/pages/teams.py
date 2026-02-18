import streamlit as st
from utils.selectors import select_league_season, LEAGUE_MAP
from utils.loader import load_json

st.set_page_config(layout="wide")

# -----------------------------
# UI
# -----------------------------
st.title("👥 Teams")

league_id, season, data_dir = select_league_season()
st.write(f"### {LEAGUE_MAP.get(league_id)} — Season {season}")

teams_data = load_json(data_dir / "teams.json")
if not teams_data:
    st.error("No teams.json found for this league/season.")
    st.stop()

# -----------------------------
# Fancy display
# -----------------------------
rows = teams_data["response"]

# metrics
countries = sorted({r["team"].get("country") for r in rows if r.get("team")})
st.caption(f"Found **{len(rows)}** teams" + (f" • Countries: {', '.join(countries)}" if countries else ""))

c1, c2 = st.columns([2, 1])
q = c1.text_input("Search team / city / venue", "")
sort_mode = c2.selectbox("Sort by", ["Team name", "Venue capacity (desc)"])

def matches(r: dict, query: str) -> bool:
    if not query:
        return True
    query = query.lower().strip()
    team = r.get("team", {}) or {}
    venue = r.get("venue", {}) or {}
    hay = " ".join([
        str(team.get("name", "")),
        str(team.get("code", "")),
        str(team.get("country", "")),
        str(venue.get("name", "")),
        str(venue.get("city", "")),
    ]).lower()
    return query in hay

view = [r for r in rows if matches(r, q)]

if sort_mode == "Team name":
    view.sort(key=lambda r: (r.get("team", {}).get("name") or "").lower())
else:
    view.sort(key=lambda r: int((r.get("venue", {}).get("capacity") or 0)), reverse=True)

st.divider()

# render as cards in a grid
cols = st.columns(3)

def fmt_int(x):
    try:
        return f"{int(x):,}".replace(",", " ")
    except Exception:
        return "-"

for i, r in enumerate(view):
    team = r.get("team", {}) or {}
    venue = r.get("venue", {}) or {}

    with cols[i % 3]:
        st.markdown(
            f"""
            <div style="
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 14px;
                padding: 12px 12px;
                margin: 8px 0;
                background: rgba(255,255,255,0.03);
            ">
              <div style="display:flex; align-items:center; gap:10px;">
                <img src="{team.get('logo')}" style="width:34px; height:34px;" />
                <div style="flex:1;">
                  <div style="font-weight:750; font-size:1.05rem;">
                    {team.get("name", "—")}
                    <span style="opacity:0.7; font-weight:500;">({team.get("code","") or "—"})</span>
                  </div>
                  <div style="opacity:0.75; font-size:0.9rem;">
                    {team.get("country","")} • Founded: {team.get("founded","—")}
                  </div>
                </div>
              </div>

              <div style="margin-top:10px; opacity:0.85; font-size:0.92rem;">
                🏟️ <b>{venue.get("name","—")}</b><br/>
                📍 {venue.get("city","—")} • Capacity: <b>{fmt_int(venue.get("capacity"))}</b> • Surface: {venue.get("surface","—")}
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # optional: venue image collapsible
        with st.expander("Venue image", expanded=False):
            img = venue.get("image")
            if img:
                st.image(img, use_container_width=True)
            else:
                st.caption("No venue image.")

if not view:
    st.info("No teams match your search.")
