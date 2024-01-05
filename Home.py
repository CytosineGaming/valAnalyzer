import streamlit as st
import streamlit.components.v1 as components
from streamlit.components.v1 import html
import dataRAW as d
import valo_api as val
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import requests

st.set_page_config(layout="wide")

with open('home.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def nav_page(page_name, match_id, timeout_secs=3, ):
    nav_script = """
        <script type="text/javascript">
            function attempt_nav_page(page_name, start_time, timeout_secs, match_id) {
                var links = window.parent.document.getElementsByTagName("a");
                for (var i = 0; i < links.length; i++) {
                    if (links[i].href.toLowerCase().endsWith("/" + page_name.toLowerCase())) {
                        links[i].href = links[i] + "?match_id=" + match_id
                        links[i].click();
                        return;
                    }
                }
                var elasped = new Date() - start_time;
                if (elasped < timeout_secs * 1000) {
                    setTimeout(attempt_nav_page, 100, page_name, start_time, timeout_secs);
                } else {
                    alert("Unable to navigate to page '" + page_name + "' after " + timeout_secs + " second(s).");
                }
            }
            window.addEventListener("load", function() {
                attempt_nav_page("%s", new Date(), %d, "%s");
            });
        </script>
    """ % (page_name, timeout_secs, match_id)
    html(nav_script)

def load_player_info(name):
    # W, L
    wins = d.get_overall_wins(name)
    losses = d.get_overall_losses(name)

    fig, ax = plt.subplots()
    wedges, texts = ax.pie([wins, losses], colors=["green", "red"], wedgeprops=dict(width = 0.2),
            startangle = 90, radius=1)
    plt.text(-0.5, .075, str(wins) + " W", fontsize=50, color="white", fontfamily="Roboto")
    plt.text(-0.5, -0.375, str(losses) + " L", fontsize=50, color="white", fontfamily="Roboto")
    plt.savefig("img/win_rate.png", transparent=True)

    stats_col1, stats_col2 = st.columns([4,3])
    with stats_col1:
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
        small_col1, small_col2, small_col3, small_col4 = st.columns(4)
        with small_col1:
            st.metric(label="Kills", value=d.get_overall_kills(name))
            st.metric(label="Kills / Round", value=d.get_overall_KPR(name))
        with small_col2:
            st.metric(label="Deaths", value=d.get_overall_deaths(name))
            st.metric(label="First Bloods", value=d.get_overall_first_bloods(name))
        with small_col3:
            st.metric(label="Assists", value=d.get_overall_assists(name))
            st.metric(label="First Blood Rate", value=d.get_overall_first_blood_rate(name))
        with small_col4:
            st.metric(label="KDA Ratio", value=d.get_overall_KDA(name))
            st.metric(label="Rounds Played", value=d.get_overall_rounds_played(name))
    
    # Accuracy STUFF
    # HS%, BS%, LS%, HS, BS, LS
    head_color, body_color, leg_color = "#808080", "#808080", "#808080"
    hs, bs, ls = d.get_overall_headshots(name), d.get_overall_bodyshots(name), d.get_overall_legshots(name)
    hsr, bsr, lsr = d.get_overall_hs_rate(name), d.get_overall_bs_rate(name), d.get_overall_ls_rate(name)
    if hsr > bsr and hsr > lsr:
        head_color = "#16e5b4"
    elif bsr > hsr and bsr > lsr:
        body_color = "#16e5b4"
    elif lsr > hsr and lsr > bsr:
        leg_color = "#16e5b4"

    with stats_col2:
        win_rate, shots_man, shots_header, shots_per, shots_total, = st.columns([4, 3, 2, 2, 2])
        with win_rate:
            win_rate_image = Image.open("img/win_rate.png")
            st.image(win_rate_image, width=200)
        with shots_man:
            components.html(""" <svg data-v-9526a87d="" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 33.316 80" class="accuracy__dummy">
                                    <g transform="translate(-636.875 -624)">
                                        <circle cx="6.153" cy="6.153" r="6.153" transform="translate(647.387 624)"
                                        fill=""" + head_color + """></circle>
                                        <path d="M6.521,41.025h0l-6.52,0L5.863,0H18.756l5.857,41.021-6.508,0L12.307,8.2,6.521,41.024Z" transform="translate(641.232 662.975)"
                                        fill=""" + leg_color + """></path>
                                        <path d="M29.285,26.472,24.17,13.678l-1.352,6.831H10.512l-1.363-6.84-5.117,12.8A2.049,2.049,0,1,1,.072,25.411L6.441,1.639l.008,0A2.055,2.055,0,0,1,8.461,0h4.1L16.67,4.1l4.1-4.1h4.111a2.048,2.048,0,0,1,2.016,1.712l6.352,23.7a2.049,2.049,0,1,1-3.959,1.061Z" transform="translate(636.875 638.36)"
                                        fill=""" + body_color + """></path>
                                    </g>
                                </svg>""", width=100, height=200)
        with shots_header:
            st.write("Head")
            st.write("Body")
            st.write("Leg")
        with shots_per:
            st.write(str(hsr))
            st.write(str(bsr))
            st.write(str(lsr))
        with shots_total:
            st.write(str(hs))
            st.write(str(bs))
            st.write(str(ls))

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

        selected_match = match_history_component(match_id=match[0], agent=d.convert_image_to_base64(player_match_info[0]), place=player_match_info[1], kills=player_match_info[2], deaths=player_match_info[3], assists=player_match_info[4],
                                ally_score=player_match_info[5], enemy_score=player_match_info[6], result=player_match_info[7], start_time=player_match_info[8], map=player_match_info[9], result_color=result_color,
                                bk_color=background_color, place_color=place_color)

        #if clicked, go to other page with timeline
        if selected_match != None:
            print(selected_match)
            nav_page("match_details", selected_match)


# WEBPAGE STUFF

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
    
