import valAnalyzer as analyzer
import valo_api as val
import pandas as pd
import Image
import requests
import BytesIO

# https://dash.valorant-api.com/endpoints/maps
def calc_percent():
    pass

def get_raw_kd_coords(game):
    all_kills = []

    for round in game.rounds:
        round_info = [round.winning_team, round.end_type, round.bomb_planted, round.bomb_defused]
        round_eventfeed = []
        for player in round.player_stats:
            for kill_event in player.kill_events:
                # time_ms = kill_event.kill_time_in_round
                # time = to_min_sec(time_ms)
                # killer = kill_event.killer_display_name
                # weapon = kill_event.damage_weapon_name
                # if weapon is None:
                #     weapon = kill_event.damage_weapon_id
                victim = kill_event.victim_display_name
                # player_info = []
                victim_death_location = [kill_event.victim_death_location.x, kill_event.victim_death_location.y]
                # for player in kill_event.player_locations_on_kill:
                #     player_info.append([player.player_display_name, player.player_team, player.location.x, player.location.y, player.view_radians])

                kill_info = ["Kill", victim_death_location]
                round_eventfeed.append(kill_info)
        all_kills.append(round_eventfeed)

    return all_kills

def heatmap_kill_coords(img, rounds):
    resp = requests.get("https://valorant-api.com/v1/maps/" + uuid)
    data = resp.json()
    img_resp = requests.get("https://media.valorant-api.com/maps/" + uuid + "/displayicon.png")
    img = Image.open(BytesIO(img_resp.content))

    map_x_multiplier = float(data["data"]["xMultiplier"])
    map_y_multiplier = float(data["data"]["yMultiplier"])
    map_x_scalar = data["data"]["xScalarToAdd"]
    map_y_scalar = data["data"]["yScalarToAdd"]

    map_death_coords = []
    for round in rounds:
        for game_x, game_y in zip(kill_event_df['deathx'], kill_event_df['deathy']):
            map_x = game_y * map_x_multiplier + map_x_scalar
            map_y = game_x * map_y_multiplier + map_y_scalar
            map_x *= img.width
            map_y *= img.height
            map_death_coords.append([map_x, map_y])
    return map_death_coords