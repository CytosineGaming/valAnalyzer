import streamlit as st
import streamlit.components.v1 as components
import dataRAW as d
import valo_api as val
import pandas as pd

def load_player_info(name):
    # W, L


    # KD, HS%, ACS, 
    big_col1, big_col2, big_col3 = st.columns(3)
    with big_col1:
        st.metric(label="KD Ratio", value=d.get_overall_KD(name))
    with big_col2:
        st.metric(label="Headshot %", value=d.get_overall_hs_rate(name))
    with big_col3:
        st.metric(label="ACS", value=d.get_overall_ACS(name))

    # K, D, A, KDA
    # KPR, FB, FD, ROUNDS
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    with stat_col1:
        st.metric(label="Kills", value=d.get_overall_kills(name))
        st.metric(label="Kills / Round", value=d.get_overall_KPR(name))
    with stat_col2:
        st.metric(label="Deaths", value=d.get_overall_deaths(name))
        st.metric(label="First Bloods", value=d.get_overall_first_bloods(name))
    with stat_col3:
        st.metric(label="Assists", value=d.get_overall_assists(name))
        st.metric(label="First Blood Rate", value=d.get_overall_first_blood_rate(name))
    with stat_col4:
        st.metric(label="KDA Ratio", value=d.get_overall_KDA(name))
        st.metric(label="Rounds Played", value=d.get_overall_rounds_played(name))

    # Accuracy STUFF
    # HS%, BS%, LS%, HS, BS, LS

    match_history_component = components.declare_component(
            "match_history_component",
            url="http://localhost:3001"
        )

    for match in matches:
        player_match_info = d.get_player_match_info(name, match) #[Agent, Scoreboard Place, Kills, Deaths, Assists, Ally Score, Enemy Score, Results, Start Time, Map]
        result_color = "#5aff7f"
        background_color = "linear-gradient(90deg, rgb(65, 156, 174) 0.00%,rgb(137, 189, 200) 120.00%)"
        place_color = "#d9d9d9"
        if player_match_info[7] == "DEFEAT":
            result_color = "#9e0b0b"
            background_color = "linear-gradient(90deg, rgb(174, 65, 65) 0.00%,rgb(200, 137, 137) 120.00%)"
        if player_match_info[1] == "MVP":
            place_color = "#f7b211"

        match_history_component(match_id=match[0], agent=d.convert_image_to_base64(player_match_info[0]), place=player_match_info[1], kills=player_match_info[2], deaths=player_match_info[3], assists=player_match_info[4],
                                ally_score=player_match_info[5], enemy_score=player_match_info[6], result=player_match_info[7], start_time=player_match_info[8], map=player_match_info[9], result_color=result_color,
                                bk_color=background_color, place_color=place_color)

# WEBPAGE STUFF
st.set_page_config(layout="wide")

st.title("Valorant Analyzer")
st.subheader("Created by Wei-Jia Chen and Shikhar Joshi")

name = st.text_input(label="RiotID #Tag", type="default", help="Enter your Riot ID and Tag. This is found in game, when you hover over your name.")
name_tag = name.replace(" #", "#").split("#")
if len(name_tag) == 2:
    name = name_tag[0] + "#" + name_tag[1]

matches = d.get_player_matches(name)
if matches == False:
    if len(name_tag) == 2 and 3 <= len(name_tag[0]) <= 16 and 3 <= len(name_tag[1]) <= 5:
        
        button_container = st.empty()
        with button_container.container():
            st.write("Valid Name")
            get_matches_button = st.button(label="Get Recent Matches")
        if get_matches_button:
            d.store_all_recent_comp_games("na", name_tag)
            button_container.empty()

            matches = d.get_player_matches(name)
            if matches != False:
                load_player_info(name)
            else:
                st.write("No Matches to Display")

    else:
        st.write("Invalid Name")
else:
    d.store_all_recent_comp_games("na", name_tag)

    if matches != False:
        load_player_info(name)
    else:
        st.write("No Matches to Display")
    
