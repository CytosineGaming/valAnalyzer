import streamlit as st
import streamlit.components.v1 as cm
import analyzer as a
import valo_api as val
import pandas as pd

st.set_page_config(page_title="valoAnalyzer", page_icon=":tada:", layout="wide")

# header
st.title("Valorant Analyzer")
st.subheader("WOW :wave:")
st.write("YOU WORK")
st.write("[link >](https://playvalorant.com)")

# slider
n = st.slider('how many matches', 1, 10, 7)

# match history
region = "na"
name = "Cytosine"
tag = "7670"
game_mode = "competitive"

recent_matches_data = a.get_recent_matches(region, name, tag, n, game_mode)
match_history = a.get_match_history(recent_matches_data, name, tag)
columns_headers = ["Match ID", "Map", "Game Start Time", "Game Length", "Result", "Score", "Load Game"]
history_table = pd.DataFrame(data=match_history, columns=columns_headers)
match_history_st_table = st.data_editor(history_table)

for match in range(len(match_history_st_table)):
    if match_history_st_table.get("Load Game")[match] == True:
        match_stats = a.get_match_stats(recent_matches_data[match])
        scoreboard_headers = ["Team", "Agent", "Name", "ACS", "Kills", "Deaths", "Assists", "Plants", "Defuses", 
                              "Headshots", "Bodyshots", "Legshots", "HS Rate", "C Casts", "Q Casts", "E Casts", "X Casts", "Ultimate Kills"]
        scoreboard = pd.DataFrame(data=match_stats, columns=scoreboard_headers)
        scoreboard_st_table = st.dataframe(scoreboard)

        round_timeline_stats = a.get_match_round_timeline(recent_matches_data[match])
        round_timeline_indexes = list(range(1, len(round_timeline_stats) + 1))
        round_timeline_headers = ["Winning Team", "End Type", "Load Round"]
        round_timeline_table = pd.DataFrame(data=round_timeline_stats, index=round_timeline_indexes, columns=round_timeline_headers)
        round_timeline_st_table = st.data_editor(round_timeline_table)

        for round in range(len(round_timeline_st_table)):
            round_events = a.to_event_timeline_table(a.get_match_event_timeline(recent_matches_data[match])[round])
            round_event_timeline_headers = ["Time", "Action", "Actor", "Weapon", "Victim"]
            round_event_timeline_table = pd.DataFrame(data=round_events, columns=round_event_timeline_headers)
            round_event_timeline_st_table = st.dataframe(round_event_timeline_table)

