# Documentation https://raimannma.github.io/ValorantAPI/index.html
# Django Models https://www.w3schools.com/django/django_insert_data.php

"""
4/2/23 - 3:51 AM
- added match history function, game stats function, and round info function

4/2/23 - ~9:00 PM
- added more functionality to game stats, create website UI to display game stats

4/3/23 - 9:58 AM
- changed game_start_time to show time in EST
"""

import valo_api as val
import datetime as dt
import analyzer.database as db

def to_min_sec(time): #converts time in ms to min:sec
    min = time // 60000
    sec = (time // 1000) - (min * 60)

    return (str(min) + ":" + str(sec).zfill(2))
    
def to_hr_min_sec(time):
    hr = time // 3600
    min = time // 60 - (hr * 60)
    sec = time - (min * 60) - (hr * 3600)
    
    return (str(hr) + ":" + str(min).zfill(2) + ":" + str(sec).zfill(2))

def get_match_history(region, name, tag, size=1, game_mode=None): #fetch games
    history = val.get_match_history_by_name_v3(region, name, tag, size, game_mode)
    return history

def get_single_match(match_id):
    return val.get_match_details_v2(match_id)

def get_single_match_info(game, name, tag):
    match_id = game.metadata.matchid
    game_map = game.metadata.map
    game_length = to_hr_min_sec(game.metadata.game_length)
    score = ""
    team = ""
    for player in game.players.all_players:
        if name == player.name and tag == player.tag:
            team = player.team
    winning_team = ""
    if game.teams.red.has_won == True:
        winning_team = "Red"
    else:
        winning_team = "Blue"
    result = "Defeat"
    if winning_team == team:
        result = "Victory"
    if team == "Red":
        score = str(game.teams.red.rounds_won) + "-" + str(game.teams.blue.rounds_won)
    else:
        score = str(game.teams.blue.rounds_won) + "-" + str(game.teams.red.rounds_won)
    time_start = dt.datetime.fromtimestamp(game.metadata.game_start - 18000)

    return [match_id, game_map, time_start, game_length, result, score]

def get_match_history_info(region, name, tag, size=1, game_mode=None):
    game_array = [] #[map, game_length, result, score, key]
    history = val.get_match_history_by_name_v3(region, name, tag, size, game_mode)

    for game in history:
        id = game.metadata.matchid
        game_map = game.metadata.map
        game_length = to_hr_min_sec(game.metadata.game_length)
        score = ""
        team = ""
        for player in game.players.all_players:
            if name == player.name and tag == player.tag:
                team = player.team
        winning_team = ""
        if game.teams.red.has_won == True:
            winning_team = "Red"
        else:
            winning_team = "Blue"
        result = "Defeat"
        if winning_team == team:
            result = "Victory"
        if team == "Red":
            score = str(game.teams.red.rounds_won) + "-" + str(game.teams.blue.rounds_won)
        else:
            score = str(game.teams.blue.rounds_won) + "-" + str(game.teams.red.rounds_won)
        time_start = dt.datetime.fromtimestamp(game.metadata.game_start - 18000)

        is_uploaded = db.check_exists(id)

        game_array.append([id, game_map, time_start, game_length, result, score, is_uploaded])
    
    return game_array

def get_game_stats(game, all_round_events): #return scoreboard stats
    stats = [] #Team, Name, ACS, K, D, A, ECON, Plants, Defuses
    rounds = game.metadata.rounds_played

    for player in game.players.all_players:
        team = player.team
        character = player.character
        name = player.name + "#" + player.tag
        acs = player.stats.score // rounds
        kills = player.stats.kills
        deaths = player.stats.deaths
        assists = player.stats.assists
        first_bloods = 0
        first_deaths = 0
        plants = 0
        defuses = 0
        headshots = player.stats.headshots
        bodyshots = player.stats.bodyshots
        legshots = player.stats.legshots
        hs_rate = (headshots * 100) // (headshots + bodyshots + legshots)
        c_uses = player.ability_casts.c_cast
        q_uses = player.ability_casts.q_cast
        e_uses = player.ability_casts.e_cast
        x_uses = player.ability_casts.x_cast
        ultimate_kills = 0

        for game_round in game.rounds:
            if game_round.bomb_planted and (game_round.plant_events.planted_by.display_name == name):
                plants += 1
            if game_round.bomb_defused and (game_round.defuse_events.defused_by.display_name == name):
                defuses += 1

        for game_round in all_round_events:
            event_type = ""
            i = -1
            while event_type != "Kill":
                i += 1
                event_type = game_round[i][2]
            if game_round[i][3] == name:
                first_bloods += 1
            if game_round[i][5] == name:
                first_deaths += 1
            
            for kill_event in game_round:
                if kill_event[2] == "Kill" and kill_event[4] == "Ultimate" and kill_event[3] == name:
                    ultimate_kills += 1
    
        player_stats = [team, character, name, acs, kills, deaths, assists, first_bloods, first_deaths, plants, defuses, headshots, bodyshots, legshots, hs_rate, c_uses, q_uses, e_uses, x_uses, ultimate_kills]

        stats.append(player_stats)

    return sorted(stats, key=lambda x:x[3], reverse=True)

def get_all_round_events(game): # [rounds][events in order]
    all_rounds = []

    for round in game.rounds:
        round_info = [round.winning_team, round.end_type, round.bomb_planted, round.bomb_defused]
        round_eventfeed = []

        if round.bomb_planted is True:
            time_ms = round.plant_events.plant_time_in_round
            time = to_min_sec(time_ms)
            planter = round.plant_events.planted_by.display_name
            site = round.plant_events.plant_site
            player_info = []
            for player in round.plant_events.player_locations_on_plant:
                player_info.append([player.player_display_name, player.player_team, player.location.x, player.location.y, player.view_radians])

            plant_info = [time_ms, time, "Plant", planter, site, player_info]
            round_eventfeed.append(plant_info)
        if round.bomb_defused is True:
            time_ms = round.defuse_events.defuse_time_in_round
            time = to_min_sec(time_ms)
            defuser = round.defuse_events.defused_by.display_name
            player_info = []
            for player in round.defuse_events.player_locations_on_defuse:
                player_info.append([player.player_display_name, player.player_team, player.location.x, player.location.y, player.view_radians])

            defuse_info = [time_ms, time, "Defuse", defuser, player_info]
            round_eventfeed.append(defuse_info)
        for player in round.player_stats:
            for kill_event in player.kill_events:
                time_ms = kill_event.kill_time_in_round
                time = to_min_sec(time_ms)
                killer = kill_event.killer_display_name
                weapon = kill_event.damage_weapon_name
                if weapon is None:
                    weapon = kill_event.damage_weapon_id
                victim = kill_event.victim_display_name
                player_info = []
                victim_death_location = [kill_event.victim_death_location.x, kill_event.victim_death_location.y]
                for player in kill_event.player_locations_on_kill:
                    player_info.append([player.player_display_name, player.player_team, player.location.x, player.location.y, player.view_radians])

                kill_info = [time_ms, time, "Kill", killer, weapon, victim, victim_death_location, player_info]
                round_eventfeed.append(kill_info)
        all_rounds.append(sorted(round_eventfeed))

    return all_rounds
        
def get_round_timeline(game): #score after each round and end_type
    timeline = []
    round_num = 0
    blue_score = 0
    red_score = 0
    
    for round in game.rounds:
        if round.winning_team == "Blue":
            blue_score += 1
        else:
            red_score += 1
        round_info = [round_num + 1, round.winning_team, round.end_type, blue_score, red_score]
        timeline.append(round_info)
        round_num += 1

    return timeline

def main():
    history = get_match_history("na", "HKR Cytosine", "7670", 1, "custom")
    for game in history:
        all_rounds = get_all_round_events(game)
        match_stats =  get_game_stats(game, all_rounds)
        for player in match_stats:
            print(player)
        print("---------- ROUND TIMELINE ----------")
        round_timeline = get_round_timeline(game)
        for round in round_timeline:
            print(round)
        print("---------- ALL ROUND INFO ----------")
        round_num = 1
        for round in all_rounds:
            print("---------- ROUND " + str(round_num) + " INFO ----------")
            for event in round:
                print(event)
            round_num += 1
        print("----------------------------------------\n\n")
        
if __name__ == "__main__":
    main()