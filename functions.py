import streamlit as st
import valo_api as val
import datetime as dt

def to_min_sec(time): #converts time in ms to min:sec
    min = time // 60000
    sec = (time // 1000) - (min * 60)

    return (str(min) + ":" + str(sec).zfill(2))
    
def to_hr_min_sec(time): #converts time in ms to hour:min:sec
    hr = time // 3600
    min = time // 60 - (hr * 60)
    sec = time - (min * 60) - (hr * 3600)
    
    return (str(hr) + ":" + str(min).zfill(2) + ":" + str(sec).zfill(2))

def get_recent_matches(region, name, tag, size, gamemode): #get most recent matches
    recent_matches = val.get_match_history_by_name_v3(region, name, tag, size, game_mode)
    return recent_matches

def get_match_info(game): #returns ID, Map, Start Time, Game Length, Result (player POV), and Score (Player POV) for a given match
    id = game.metadata.matchid #match ID
    game_map = game.metadata.map #match map
    game_length = to_hr_min_sec(game.metadata.game_length) #get length of game in hr:min:sec
    time_start = dt.datetime.fromtimestamp(game.metadata.game_start - 18000) #exact time in Eastern Time

    team = "" #team player is on
    for player in game.players.all_players: #find team value of searched player and assign to "team"
        if name == player.name and tag == player.tag:
            team = player.team

    winning_team = "" #winning team ("Red" or "Blue")
    if game.teams.red.has_won == True:
        winning_team = "Red"
    else:
        winning_team = "Blue"

    score = "" #final game score
    result = "Defeat" #result of game based on who won
    if winning_team == team:
        result = "Victory"
    if team == "Red":
        score = str(game.teams.red.rounds_won) + "-" + str(game.teams.blue.rounds_won) #"Red score - Blue Score" if player is on red
    else:
        score = str(game.teams.blue.rounds_won) + "-" + str(game.teams.red.rounds_won) #"Blue score - Red Score" if player is on blue

    return [id, game_map, time_start, game_length, result, score]

def get_match_history(recent_matches): #get ID, Map, Start Time, Game Length, Result (player POV), and Score (Player POV) for all recent matches
    game_array = [] #[map, game_length, result, score, key]

    for game in recent_matches: #loop through every match played
        game_array.append(get_match_info(game)) #add row to game_array with game information to be displayed

    return game_array

def get_match_stats(game): #get for every player: [Team, Player Name, Player Tag, ACS, K, D, A, ECON, Plants, Defuses, Headshots, Bodyshots, Legshots, HS rate, C, Q, E, X, X Kills]
    stats = [] #array of statistics
    rounds = game.metadata.rounds_played #num of rounds played
    event_timeline = get_match_event_timeline(game) #get event timeline [round][events in order]

    for player in game.players.all_players: #loop through every player in the game
        team = player.team #read team value
        character = player.character #agent played
        name = player.name #player name
        tag = player.tag #player tag
        acs = player.stats.score // rounds #ACS = Total Score / Rounds (to nearest int)
        kills = player.stats.kills #number of kills
        deaths = player.stats.deaths #number of deaths
        assists = player.stats.assists #number of assists
        headshots = player.stats.headshots #number of hs
        bodyshots = player.stats.bodyshots #number of bodyshots
        legshots = player.stats.legshots #number of legshots
        hs_rate = (headshots * 100) // (headshots + bodyshots + legshots) #hs rate (hs vs all connected shots)
        c_uses = player.ability_casts.c_cast #number of C casts
        q_uses = player.ability_casts.q_cast #number of Q casts
        e_uses = player.ability_casts.e_cast #number of E casts
        x_uses = player.ability_casts.x_cast #number of ult casts
        ultimate_kills = 0 #number of ult kills

        first_bloods = 0 #number of FB
        first_deaths = 0 #number of FD
        for game_round in event_timeline: #for every round
            event_type = "" #
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

        plants = 0 #number of plants
        defuses = 0 #number of defuses
        for game_round in game.rounds: #count number of plants and defuses by player
            if game_round.bomb_planted and (game_round.plant_events.planted_by.display_name == name):
                plants += 1
            if game_round.bomb_defused and (game_round.defuse_events.defused_by.display_name == name):
                defuses += 1

def get_match_event_timeline(game): # [rounds][events in order]
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

def get_match_round_timeline(game): #[Round Num, Winning Team, End Type, Cumulative Blue Score, Cumulative Red Score]
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
