import analyzer.models as m
import analyzer.valAnalyzer as val

def check_exists(match_id):
    game_info = m.GameInfo.objects.all()
    print(game_info)
    return False

def upload_match(match_id, name, tag):
    game = val.get_single_match(match_id)
    game_info = val.get_single_match_info(game, name, tag)
    game_round_event = val.get_all_round_events(game)
    game_scoreboard = val.get_game_stats(game, game_round_event)
    game_round_timeline = val.get_round_timeline(game)

    db_game_info = m.GameInfo(matchid=match_id, map=game_info[1], time_start=game_info[2], 
                              game_length=game_info[3], result=game_info[4], score=game_info[5])
    db_game_info.save()

    for player in game_scoreboard: 
        db_player_scoreboard = m.GameStats(matchid=match_id, team=player[0], character=player[1],
                                          name=player[2], acs=player[3], kills=player[4],
                                          deaths=player[5], assists=player[6], first_bloods=player[7],
                                          first_deaths=player[8], plants=player[9], defuses=player[10], 
                                          headshots=player[11], bodyshots=player[12], legshots=player[13], 
                                          hs_rate=player[14], c_uses=player[15], q_uses=player[16], 
                                          e_uses=player[17], x_uses=player[18], ultimate_kills=player[19])
        db_player_scoreboard.save()

    for round in game_round_timeline:
        db_single_round_timeline = m.GameTimeline(matchid=match_id, round=round[0], winning_team=round[1], end_type=round[2])
        db_single_round_timeline.save()

    for round in game_round_event:
        round_num = 1
        for event in round:
            db_single_round_event = None
            if event[2] == "Kill": #[timems, time, "Kill", killer, weapon, victim, [victimx, victimy], player_info]
                db_single_round_event = m.GameRounds(matchid=match_id, round=round_num, time_ms=event[0], 
                                                   time=event[1], event_type=event[2], performer=event[3], 
                                                   site="None", weapon=event[4], victim=event[5], 
                                                   victim_death_loc_x=event[6][0], victim_death_loc_y=event[6][1])
                for player in event[7]: #[name, team, locx, locy, viewrad]
                    db_player_round_info = m.GamePlayerInfo(matchid=match_id, round=round_num, time_ms=event[0],
                                                            player_name=player[0], player_team=player[1], player_loc_x=player[2],
                                                            player_loc_y=player[3], player_loc_angle=player[4])
                    db_player_round_info.save()

            elif event[2] == "Plant": #[timems, time, "Plant", planter, site, "player_info]
                db_single_round_event = m.GameRounds(matchid=match_id, round=round_num, time_ms=event[0], 
                                                   time=event[1], event_type=event[2], performer=event[3], 
                                                   site=event[4], weapon="None", victim="None", 
                                                   victim_death_loc_x=0, victim_death_loc_y=0)
                for player in event[5]: #[name, team, locx, locy, viewrad]
                    db_player_round_info = m.GamePlayerInfo(matchid=match_id, round=round_num, time_ms=event[0],
                                                            player_name=player[0], player_team=player[1], player_loc_x=player[2],
                                                            player_loc_y=player[3], player_loc_angle=player[4])
                    db_player_round_info.save()

            else: #event[2] = "Defuse" [timems, time, "Defuse", defuser, "player_info]
                db_single_round_event = m.GameRounds(matchid=match_id, round=round_num, time_ms=event[0], 
                                                   time=event[1], event_type=event[2], performer=event[3], 
                                                   site="None", weapon="None", victim="None", 
                                                   victim_death_loc_x=0, victim_death_loc_y=0)
                for player in event[4]: #[name, team, locx, locy, viewrad]
                    db_player_round_info = m.GamePlayerInfo(matchid=match_id, round=round_num, time_ms=event[0],
                                                            player_name=player[0], player_team=player[1], player_loc_x=player[2],
                                                            player_loc_y=player[3], player_loc_angle=player[4])
                    db_player_round_info.save()

            db_single_round_event.save()

        round_num += 1