import streamlit as st
import streamlit.components.v1 as cm
import valAnalyzer as analyzer
import valo_api as val
import pandas as pd

st.set_page_config(page_title="valoAnalyzer", page_icon=":tada:", layout="wide")

# header
st.subheader("this is a subheader :wave:")
st.title("this is a title")
st.write("this is a paragraph")
st.write("[link >](https://playvalorant.com)")

# slider
n = st.slider('how many matches', 1, 10, 7)

# buttons
history_info = analyzer.get_match_history_info("na", "HKR Cytosine", "7670", n, "custom")
game_data = analyzer.get_match_history("na", "HKR Cytosine", "7670", n, "custom")
columns = ["Map", "Game Length", "Result", "Score", "Load Game"]
history_table = pd.DataFrame(data=history_info, columns=columns)
new_table = st.experimental_data_editor(history_table)

for i in range(len(new_table)):
    if new_table.get("Load Game")[i] == True:
        all_rounds = analyzer.get_all_round_events(game_data[i])
        match_stats =  analyzer.get_game_stats(game_data[i], all_rounds)
        scoreboard = pd.DataFrame(match_stats, columns=["Team", "Agent", "Name", "ACS", "K", "D", "A", "First Bloods", "First Deaths", "Plants", "Defuses", "Headshots", 
                                                        "Body Shots", "Leg Shots", "HS %", "C Uses", "Q Uses", "E Uses", "X Uses", "Ultimate Kills"])
        st.write(scoreboard)

# buttons w/ html
# history = analyzer.get_match_history_info("na", "HKR Cytosine", "7670", n, "custom")
# with open("gameHistory.html", 'r') as f:
#     html_string = f.read()
# for game in history:
#     cm.html(html_string, height = 500)

# get_match_history listener
# if get_match_history_button is True:
#     for df in scoreboard_arr:
#         st.write(df)
# else:

