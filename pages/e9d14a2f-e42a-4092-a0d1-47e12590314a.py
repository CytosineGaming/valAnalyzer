import streamlit as st
from streamlit.components.v1 import html
import dataRAW as d
import pandas as pd

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)

match_id = "e9d14a2f-e42a-4092-a0d1-47e12590314a"
selected_round = 1

def ms_to_time(time):
    seconds = (time // 1000) % 60
    minutes = (time // 60000)

    if seconds < 10:
        return str(minutes) + ":0" + str(seconds)
    else:
        return str(minutes) + ":" + str(seconds)

def select_round(round_num):
    selected_round = round_num
    round_events = d.get_round_events(match_id, selected_round)
    return round_events

def format_events(round_events):
    events = []
    for event in round_events:
        time = ms_to_time(event[0])
        actor = event[2]
        victim = event[4]
        if event[1] == "Plant":
            weapon = "Plant"
        elif event[1] == "Defuse":
            weapon = "Defuse"
        else:
            weapon = event[3]

        events.append([time, actor, weapon, victim])

    return events

match_info = d.get_match_info(match_id)
rounds = match_info[3] + match_info[4]

if match_info[3] > match_info[4]:
    st.markdown(""":green[**Defenders: """ + str(match_info[3]) + """**]  
                :red[Attackers: """ + str(match_info[4]) + """]  
                Map: """ + match_info[0] + """  
                Start Time: """ + match_info[1] + """  
                Match Length: """ + match_info[2])
else:
    st.markdown(""":green[Defenders: """ + str(match_info[3]) + """]  
                :red[**Attackers: """ + str(match_info[4]) + """**]  
                Map: """ + match_info[0] + """  
                Start Time: """ + match_info[1] + """  
                Match Length: """ + match_info[2])

match_stats = d.get_match_scoreboard(match_id)

scoreboard_cols = st.columns([0.45,0.4,0.15], gap="small")

with scoreboard_cols[0]:
    scoreboard_headers = ["Team", "Agent", "Name", "ACS", "Kills", "Deaths", "Assists", "First Bloods", "First Deaths", "Plants", "Defuses"]
    scoreboard = pd.DataFrame(data=match_stats, columns=scoreboard_headers)
    scoreboard_st_table = st.dataframe(scoreboard, column_config={}, hide_index=True)

round_timeline_data = d.get_match_round_timeline(match_id)
if rounds > 24:
    columns = rounds + 2
else:
    columns = rounds + 1
round_timeline = st.columns(rounds + 2)
round_num = 0
for col in range(columns):
    with round_timeline[col]:
        if col == 12 or rounds > 24 and col == 24:
            st.markdown("""##""")
            st.markdown("""##""")
            st.markdown("""###""")
            st.image("pages/timeline_images/swap.png")
        else:
            team = round_timeline_data[round_num][1]
            end_type = round_timeline_data[round_num][2]

            if st.button(str(round_timeline_data[round_num][0]), use_container_width=True):
                with scoreboard_cols[1]:
                    round_event_headers = ["Time", "Actor", "Weapon", "Victim"]
                    round_event_board = pd.DataFrame(data=format_events(select_round(round_num+1)), columns=round_event_headers)
                    round_event_table = st.dataframe(round_event_board, column_config={}, hide_index=True)

            icon = "pages/timeline_images/"
            match end_type:
                case "Eliminated":
                    icon += "elim_"
                case "Bomb defused":
                    icon += "defuse_"
                case "Bomb detonated":
                    icon += "bomb_"
                case "Round timer expired":
                    icon += "time_"
            if team == "Blue":
                icon += "win.png"
                st.image(icon)
                st.image("pages/timeline_images/dot.png")
            else:
                icon += "loss.png"
                st.image("pages/timeline_images/dot.png")
                st.image(icon)
        
            round_num += 1
