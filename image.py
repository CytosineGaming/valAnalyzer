import analyzer
import valo_api as val
import pandas as pd
import Image
import requests
import BytesIO

# [{"uuid":"7eaecc1b-4337-bbf6-6ab9-04b8f06b3319","displayName":"Ascent","narrativeDescript
# ,{"uuid":"d960549e-485c-e861-8d71-aa9d1aed12a2","displayName":"Split","narr
# ,{"uuid":"b529448b-4d60-346e-e89e-00a4c527a405","displayName":"Fracture","narrativeDescriptio
# {"uuid":"2c9d57ec-4431-9c5e-2939-8f9ef6dd5cba","displayName":"Bind","narrativ
# ,{"uuid":"2fb9a4fd-47b8-4e7d-a969-74b4046ebd53","displayName":"Breeze",
# "uuid":"92584fbe-486a-b1b2-9faa-39b0f486b498","displayName":"Sunset",
# {"uuid":"fd267378-4d1d-484f-ff52-77821ed10dc2","displayName":"Pearl","n
# {"uuid":"e2ad5c54-4114-a870-9641-8ea21279579a","displayName":"Icebox","narrativeDescription
# {"uuid":"2bee0dc9-4ffe-519b-1cbd-7fbe763a6047","displayName":"Haven",


# https://dash.valorant-api.com/endpoints/maps
def calc_percent():
    pass

def get_raw_kill_coords(game):
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
                # victim = kill_event.victim_display_name
                # player_info = []
                victim_death_location = [kill_event.victim_death_location.x, kill_event.victim_death_location.y]
                # for player in kill_event.player_locations_on_kill:
                #     player_info.append([player.player_display_name, player.player_team, player.location.x, player.location.y, player.view_radians])

                kill_info = [victim_death_location]
                round_eventfeed.append(kill_info)
        all_kills.append(round_eventfeed)

    return all_kills

def process_kill_coords(img, rounds, uuid):
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
        for game_xy in rounds[round][0]:
            game_x = game_xy[0]
            game_y = game_xy[1]
            map_x = game_y * map_x_multiplier + map_x_scalar
            map_y = game_x * map_y_multiplier + map_y_scalar
            map_x *= img.width
            map_y = (1 - map_y) * img.height
            map_death_coords.append([map_x, map_y])
    return map_death_coords

def main():
    history = analyzer.get_match_history("na", "Cytosine", "7670", 1, "competitive")
    kills = get_raw_kill_coords(history[0])


if __name__ == "__main__":
    main()