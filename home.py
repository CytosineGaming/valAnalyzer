import streamlit as st
import streamlit.components.v1 as components
import dataRAW as d
import valo_api as val
import pandas as pd

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
                match_history_component = components.declare_component(
                    "match_history_component",
                    url="http://localhost:3001"
                )

                for match in matches:
                    player_match_info = d.get_player_match_info(name, match) #[Agent, Scoreboard Place, Kills, Deaths, Assists, Ally Score, Enemy Score, Results, Start Time, Map]
                    match_history_component(agent=d.convert_image_to_base64(player_match_info[0]), place=player_match_info[1], kills=player_match_info[2], deaths=player_match_info[3], assists=player_match_info[4],
                                            ally_score=player_match_info[5], enemy_score=player_match_info[6], result=player_match_info[7], start_time=player_match_info[8], map=player_match_info[9])
            else:
                st.write("No Matches to Display")

    else:
        st.write("Invalid Name")
else:
    d.store_all_recent_comp_games("na", name_tag)

    if matches != False:
        match_history_component = components.declare_component(
            "match_history_component",
            url="http://localhost:3001"
        )

        for match in matches:
            player_match_info = d.get_player_match_info(name, match) #[Agent, Scoreboard Place, Kills, Deaths, Assists, Ally Score, Enemy Score, Results, Start Time, Map]
            match_history_component(agent=d.convert_image_to_base64(player_match_info[0]), place=player_match_info[1], kills=player_match_info[2], deaths=player_match_info[3], assists=player_match_info[4],
                                    ally_score=player_match_info[5], enemy_score=player_match_info[6], result=player_match_info[7], start_time=player_match_info[8], map=player_match_info[9])
    else:
        st.write("No Matches to Display")


    
