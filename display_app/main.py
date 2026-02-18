import streamlit as st
from pathlib import Path
from utils.selectors import select_league_season

st.set_page_config(page_title="Football Data Explorer", layout="wide")

st.title("⚽ Football Data Explorer")

# Select league + season
league_id, season, data_dir = select_league_season()

st.sidebar.success(f"League: {league_id} | Season: {season}")

st.write("### Welcome!")
st.write("Select a page from the left menu to start exploring the dataset.")
