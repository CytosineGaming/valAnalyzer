# Documentation https://raimannma.github.io/ValorantAPI/index.html

"""
4/2/23 - 3:51 AM
- added match history function, game stats function, and round info function
"""

import valo_api as val

def get_match_history(region, name, tag, size=1, game_mode=None):
    history = val.get_match_history_by_name_v3(region, name, tag, size, game_mode)
    return history

def get_game_stats(game):
    stats = [] #Team, Name, ACS, K, D, A
    rounds = game.metadata.rounds_played

    
    for i in range(5): #red team
        player_stats = []
        
        player_stats.append("red")
        player_stats.append(game.players.red[i].name)
        player_stats.append(round(game.players.red[i].stats.score / rounds))
        player_stats.append(game.players.red[i].stats.kills)
        player_stats.append(game.players.red[i].stats.deaths)
        player_stats.append(game.players.red[i].stats.assists)

        stats.append(player_stats)

    for i in range(5): #blue team
        player_stats = []
        
        player_stats.append("blue")
        player_stats.append(game.players.blue[i].name)
        player_stats.append(round(game.players.blue[i].stats.score / rounds))
        player_stats.append(game.players.blue[i].stats.kills)
        player_stats.append(game.players.blue[i].stats.deaths)
        player_stats.append(game.players.blue[i].stats.assists)

        stats.append(player_stats)
    
    return stats

def get_round_info(game, round_num):
    round = game.rounds[round_num] #MatchRoundV3

    round_info = [round.winning_team, round.end_type, round.bomb_planted, round.bomb_defused]
    round_eventfeed = []

    if round.bomb_planted == True:
        plant_info = [round.plant_events.plant_time_in_round // 1000, round.plant_events.planted_by.display_name, round.plant_events.plant_site]
        round_eventfeed.append(plant_info)
    if round.bomb_defused == True:
        defuse_info = [round.defuse_events.defuse_time_in_round // 1000, round.defuse_events.defused_by.display_name]
        round_eventfeed.append(defuse_info)
    for player in round.player_stats:
        for kill_event in player.kill_events:
            kill_info = [kill_event.kill_time_in_round // 1000, kill_event.killer_display_name, kill_event.damage_weapon_name, kill_event.victim_display_name]
            round_eventfeed.append(kill_info)

    return sorted(round_eventfeed)
        
def get_round_timeline(game):
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
        match_stats =  get_game_stats(game)
        for player in match_stats:
            print(player)
        print("---------- ROUND TIMELINE ----------")
        round_timeline = get_round_timeline(game)
        for round in round_timeline:
            print(round)
        print("---------- ROUND 2 INFO ----------")
        round_info = get_round_info(game, 1)
        for event in round_info:
            print(event)
        print("----------------------------------------\n\n")
        
if __name__ == "__main__":
    main()