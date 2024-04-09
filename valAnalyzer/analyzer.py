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

def get_recent_matches(region, name, tag, **kwargs): #get most recent matches as array (region, name, tag, size, map, game_mode)
    recent_matches = val.get_match_history_by_name_v3(region=region, name=name, tag=tag, size=kwargs.get("size", None), map=kwargs.get("map", None), game_mode=kwargs.get("game_mode", None))
    return recent_matches

def get_match_info(game): #returns ID, Map, Start Time, Game Length, Red Score, Blue Score
    id = game.metadata.matchid #match ID
    game_map = game.metadata.map #match map
    game_length = to_hr_min_sec(game.metadata.game_length) #get length of game in hr:min:sec
    time_start = dt.datetime.fromtimestamp(game.metadata.game_start - 18000) #exact time in Eastern Time

    red_score = game.teams.red.rounds_won
    blue_score = game.teams.blue.rounds_won

    return [id, game_map, time_start.strftime("%Y-%m-%d %H:%M:%S"), game_length, red_score, blue_score]

def get_match_history(recent_matches, name, tag): #get ID, Map, Start Time, Game Length, Result (player POV), and Score (Player POV) for all recent matches
    game_array = [] #[map, game_length, result, score, key]

    for game in recent_matches: #loop through every match played
        game_array.append(get_match_info(game, name, tag)) #add row to game_array with game information to be displayed

    return game_array

def get_match_stats(game): #get for every player: [Team, Agent, Player Name, Player Tag, Score, K, D, A, Plants, Defuses, Headshots, Bodyshots, Legshots, HS rate, C, Q, E, X, Rounds]
    stats = [] #array of statistics
    event_timeline = get_match_event_timeline(game) #get event timeline [round][events in order]
    rounds = len(event_timeline)

    for player in game.players.all_players: #loop through every player in the game
        team = player.team #read team value
        character = player.character #agent played
        name = player.name + "#" + player.tag #player name
        score = player.stats.score #ACS = Total Score / Rounds (to nearest int)
        kills = player.stats.kills #number of kills
        deaths = player.stats.deaths #number of deaths
        assists = player.stats.assists #number of assists
        headshots = player.stats.headshots #number of hs
        bodyshots = player.stats.bodyshots #number of bodyshots
        legshots = player.stats.legshots #number of legshots
        c_uses = player.ability_casts.c_cast #number of C casts
        q_uses = player.ability_casts.q_cast #number of Q casts
        e_uses = player.ability_casts.e_cast #number of E casts
        x_uses = player.ability_casts.x_cast #number of ult casts

        first_bloods = 0 #number of FB
        first_deaths = 0 #number of FD
        for game_round in event_timeline: #for every round
            i = 0
            while game_round[i][2] != "Kill": #find first kill
                print("---" + str(i) + "---")
                print(game_round)
                i += 1
            if game_round[i][4] == name:
                first_bloods += 1
            elif game_round[i][6] == name:
                first_deaths += 1

        plants = 0 #number of plants
        defuses = 0 #number of defuses
        for game_round in game.rounds: #count number of plants and defuses by player
            if game_round.bomb_planted and (game_round.plant_events.planted_by.display_name == name):
                plants += 1
            if game_round.bomb_defused and (game_round.defuse_events.defused_by.display_name == name):
                defuses += 1
        
        stats.append([team, character, name, score, kills, deaths, assists, first_bloods, first_deaths, plants, defuses, headshots, bodyshots, legshots, c_uses, q_uses, e_uses, x_uses, rounds])
    return sorted(stats, key=lambda x: x[3], reverse=True)

def get_match_event_timeline(game): # [rounds][events in order][time_ms, time, action, player_info, actor, weapon, victim, actor_coords, victim_coords]
    all_rounds = []

    for round in game.rounds:
        round_eventfeed = []

        if round.bomb_planted is True:
            time_ms = round.plant_events.plant_time_in_round
            time = to_min_sec(time_ms)
            planter = round.plant_events.planted_by.display_name
            site = round.plant_events.plant_site
            player_info = []
            actor_location = []
            for player in round.plant_events.player_locations_on_plant:
                player_info.append([player.player_display_name, player.player_team, player.location.x, player.location.y, player.view_radians])
                if player.player_display_name == planter:
                    actor_location = [player.location.x, player.location.y]

            plant_info = [time_ms, time, "Plant", player_info, planter, site, actor_location]
            round_eventfeed.append(plant_info)

        if round.bomb_defused is True:
            time_ms = round.defuse_events.defuse_time_in_round
            time = to_min_sec(time_ms)
            defuser = round.defuse_events.defused_by.display_name
            player_info = []
            actor_location = []
            for player in round.defuse_events.player_locations_on_defuse:
                player_info.append([player.player_display_name, player.player_team, player.location.x, player.location.y, player.view_radians])
                if player.player_display_name == defuser:
                    actor_location = [player.location.x, player.location.y]

            defuse_info = [time_ms, time, "Defuse", player_info, defuser, actor_location]
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
                actor_location = [None, None]
                victim_death_location = [kill_event.victim_death_location.x, kill_event.victim_death_location.y]
                for player in kill_event.player_locations_on_kill:
                    player_info.append([player.player_display_name, player.player_team, player.location.x, player.location.y, player.view_radians])
                    if player.player_display_name == killer:
                        actor_location = [player.location.x, player.location.y]

                kill_info = [time_ms, time, "Kill", player_info, killer, weapon, victim, actor_location, victim_death_location]
                round_eventfeed.append(kill_info)
        all_rounds.append(sorted(round_eventfeed))
    return all_rounds

def to_event_timeline_table(match_event_timeline_round): # [events][Time, Killer, Weapon, Victim]
    timeline_table = []
    for event in match_event_timeline_round:
        if event[2] == "Kill":
            timeline_table.append([event[1], event[2], event[3], event[4], event[5]]) #Time, "Kill", Killer, Weapon, Victim
        elif event[2] == "Plant":
            timeline_table.append([event[1], event[2], event[3], "", ""]) #Time, "Plant", Planter
        elif event[2] == "Defuse":
            timeline_table.append([event[1], event[2], event[3], "", ""]) #Time, "Defuse", Defuser
    return timeline_table

def get_match_round_timeline(game): #[Winning Team, End Type]
    timeline = []
    
    for round in game.rounds:
        round_info = [round.winning_team, round.end_type]
        timeline.append(round_info)

    return timeline
    
def main():
    recent_matches = get_recent_matches("na", "Cytosine", "7670", size=10, game_mode="competitive")
    for game in recent_matches:
        print(get_match_info(game))
    print("-------------------------------------------")
    recent_matches = get_recent_matches("na", "Cytosine", "7670", size=10, game_mode="competitive", map="Ascent")
    for game in recent_matches:
        print(get_match_info(game))
        # event_timeline = get_match_event_timeline(game)
        # match_stats =  get_match_stats(game)
        # for player in match_stats:
        #     print(player)
        # print("---------- ROUND TIMELINE ----------")
        # round_timeline = get_match_round_timeline(game)
        # for round in round_timeline:
        #     print(round)
        # print("---------- ALL ROUND INFO ----------")
        # round_num = 1
        # for round in event_timeline:
        #     print("---------- ROUND " + str(round_num) + " INFO ----------")
        #     for event in round:
        #         print(event)
        #     round_num += 1
        # print("----------------------------------------\n\n")
        
if __name__ == "__main__":
    main()