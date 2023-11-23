import analyzer as a
import sqlite3
import datetime as dt
import base64

def create_databases(): # Creates MatchInfo, Scoreboards, RoundTimeline, RoundEvents, RoundEventLocations
    sqliteConnection = sqlite3.connect('valAnalyzer.db')
    cursor = sqliteConnection.cursor()

    #Create Match Info Table
    query = """CREATE TABLE MatchInfo (match_id varchar(40), map varchar(15), start_time datetime, game_length time, red_score int(2), blue_score int(2))"""
    cursor.execute(query)
    
    #Create Match Scoreboard Table
    query = """CREATE TABLE Scoreboards (match_id varchar(40), team varchar(4), agent varchar (15), name varchar(25), score int(6), 
                                        kills int(4), deaths int(4), assists int(4), first_bloods int(4), first_deaths int(4), plants int(3), defuses int(3), 
                                        headshots int(5), bodyshots int(5), legshots int(5), c_casts int(3), q_casts int(3), e_casts int(3), x_casts int(3), rounds_played int(3))"""
    cursor.execute(query)

    #Create Match Rounds Table
    query = """CREATE TABLE RoundTimeline (match_id varchar(40), round_num int(3), winning_team varchar(4), end_type varchar (15))"""
    cursor.execute(query)

    #Create Match Round Events Table
    query = """CREATE TABLE RoundEvents (match_id varchar(40), round_num int(3), time_ms int(7), action varchar(6), actor varchar(25), weapon varchar(15), victim varchar(25),
                                        actor_x int(5), actor_y int(5), victim_death_x int(5), victim_death_y int(5))"""
    cursor.execute(query)

    #Create Round Event Locations Table
    query = """CREATE TABLE RoundEventLocations (match_id varchar(40), round_num int(3), time_ms int(7),
                    player_name varchar(25), player_team varchar(4), player_x int(5), player_y int(5), player_rad float(4))"""
    cursor.execute(query)

def store_all_recent_comp_games(region, name_tag): # Puts all recent comp games (not alr in database) into database
    recent_matches = a.get_recent_matches(region, name_tag[0], name_tag[1], size=10, game_mode="competitive")
    for game in recent_matches:
        store_game_file(game)

def store_game_file(game): # Stores game if not already in DB
    sqliteConnection = sqlite3.connect('valAnalyzer.db')
    cursor = sqliteConnection.cursor()

    #check if game is already in database
    match_info = a.get_match_info(game) #[ID, Map, Start Time, Game Length, Red Score, Blue Score]
    query = """SELECT (match_id) FROM MatchInfo"""
    cursor.execute(query)
    match_ids = cursor.fetchall()
    match_exists = False
    for match in match_ids:
        if match[0] == match_info[0]:
            match_exists = True

    if match_exists == False:
        #insert into Match Info
        query = """INSERT INTO MatchInfo VALUES (?, ?, ?, ?, ?, ?)"""
        cursor.execute(query, (str(match_info[0]), match_info[1], match_info[2], match_info[3], str(match_info[4]), str(match_info[5])))

        #insert into Match Scoreboard
        match_scoreboard = a.get_match_stats(game) #[Team, Agent, Player Name, Player Tag, ACS, K, D, A, Plants, Defuses, Headshots, Bodyshots, Legshots, C, Q, E, X, Rounds
        for player in match_scoreboard:
            query = """INSERT INTO Scoreboards VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
            cursor.execute(query, (match_info[0], player[0], player[1], player[2], player[3], str(player[4]), str(player[5]), str(player[6]), str(player[7]), str(player[8]),
                                str(player[9]), str(player[10]), str(player[11]), str(player[12]), str(player[13]), str(player[14]), str(player[15]), str(player[16]), str(player[17]), str(player[18])))

        #insert into Match Round Timeline
        match_round_timeline = a.get_match_round_timeline(game)
        for round in range(len(match_round_timeline)):
            query = """INSERT INTO RoundTimeline VALUES (?, ?, ?, ?)"""
            cursor.execute(query, (str(match_info[0]), str(round + 1), match_round_timeline[round][0], match_round_timeline[round][1]))

        #insert into Match Round Events and Round Event Locations
        match_round_events = a.get_match_event_timeline(game)
        for round in range(len(match_round_events)):
            for event in match_round_events[round]:
                if event[2] == "Kill":
                    query = """INSERT INTO RoundEvents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                    cursor.execute(query, (str(match_info[0]), str(round + 1), str(event[0]), event[2], event[4], event[5], event[6], str(event[7][0]), str(event[7][1]), str(event[8][0]), str(event[8][1])))
                elif event[2] == "Plant":
                    query = """INSERT INTO RoundEvents (match_id, round_num, time_ms, action, actor, actor_x, actor_y) VALUES (?,?,?,?,?,?,?)"""
                    cursor.execute(query, (str(match_info[0]), str(round + 1), str(event[0]), event[2], event[4], str(event[6][0]), str(event[6][1])))
                elif event[2] == "Defuse":
                    query = """INSERT INTO RoundEvents (match_id, round_num, time_ms, action, actor, actor_x, actor_y) VALUES (?,?,?,?,?,?,?)"""
                    cursor.execute(query, (str(match_info[0]), str(round + 1), str(event[0]), event[2], event[4], str(event[5][0]), str(event[5][1])))

                for player in event[3]:
                    query = """INSERT INTO RoundEventLocations VALUES (?,?,?,?,?,?,?,?)"""
                    cursor.execute(query, (str(match_info[0]), str(round + 1), str(event[0]), player[0], player[1], str(player[2]), str(player[3]), str(player[4])))

    #close connection and save changes
    sqliteConnection.commit()
    sqliteConnection.close()

def get_overall_kills(name): # Gets Overall Kills
    sqliteConnection = sqlite3.connect('valAnalyzer.db')
    cursor = sqliteConnection.cursor()

    query = """SELECT kills FROM Scoreboards WHERE name = ?"""
    cursor.execute(query, (name,))

    match_list = cursor.fetchall()
    total_kills = 0
    for match in match_list:
        total_kills += match[0]

    return total_kills

def get_overall_deaths(name): # Gets Overall Deaths
    sqliteConnection = sqlite3.connect('valAnalyzer.db')
    cursor = sqliteConnection.cursor()

    query = """SELECT deaths FROM Scoreboards WHERE name = ?"""
    cursor.execute(query, (name,))

    match_list = cursor.fetchall()
    total_deaths = 0
    for match in match_list:
        total_deaths += match[0]

    return total_deaths

def get_overall_assists(name): # Gets Overall Assists
    sqliteConnection = sqlite3.connect('valAnalyzer.db')
    cursor = sqliteConnection.cursor()

    query = """SELECT assists FROM Scoreboards WHERE name = ?"""
    cursor.execute(query, (name,))

    match_list = cursor.fetchall()
    total_assists = 0
    for match in match_list:
        total_assists += match[0]

    return total_assists

def get_overall_rounds_played(name): # Gets Overall Rounds Played
    sqliteConnection = sqlite3.connect('valAnalyzer.db')
    cursor = sqliteConnection.cursor()

    query = """SELECT rounds_played FROM Scoreboards WHERE name = ?"""
    cursor.execute(query, (name,))

    match_list = cursor.fetchall()
    total_rounds_played = 0
    for match in match_list:
        total_rounds_played += match[0]

    return total_rounds_played

def get_overall_KD(name): # Gets Overall KD
    kills = get_overall_kills(name)
    deaths = get_overall_deaths(name)

    return kills / deaths

def get_overall_KDA(name): # Get Overall KDA
    kills = get_overall_kills(name)
    deaths = get_overall_deaths(name)
    assists = get_overall_assists(name)

    return (kills + assists)/deaths

def get_overall_win_percent(name): # Get Overall Win Percentage (out of 100)
    sqliteConnection = sqlite3.connect('valAnalyzer.db')
    cursor = sqliteConnection.cursor()

    #get team with match ID
    query = """SELECT match_id, team FROM Scoreboards WHERE name = ?"""
    cursor.execute(query, (name,))
    player_data = cursor.fetchall()
    wins = 0
    losses = 0

    for match in player_data:
        query = """SELECT blue_score, red_score FROM MatchInfo WHERE match_id = ?"""
        cursor.execute(query, (match[0],))
        results = cursor.fetchall()

        if results[0][0] > results[0][1] and match[1] == "Blue":
            wins += 1
        elif results[0][0] < results[0][1] and match[1] == "Red":
            wins += 1
        else:
            losses += 1

    return 100.0 * wins / (wins + losses)

def get_overall_first_bloods(name): # Gets Overall First Bloods
    sqliteConnection = sqlite3.connect('valAnalyzer.db')
    cursor = sqliteConnection.cursor()

    query = """SELECT first_bloods FROM Scoreboards WHERE name = ?"""
    cursor.execute(query, (name,))

    match_list = cursor.fetchall()
    total_fb = 0
    for match in match_list:
        total_fb += match[0]

    return total_fb

def get_overall_first_deaths(name): # Gets Overall First Deaths
    sqliteConnection = sqlite3.connect('valAnalyzer.db')
    cursor = sqliteConnection.cursor()

    query = """SELECT first_deaths FROM Scoreboards WHERE name = ?"""
    cursor.execute(query, (name,))

    match_list = cursor.fetchall()
    total_fd = 0
    for match in match_list:
        total_fd += match[0]

    return total_fd

def get_overall_headshots(name): # Gets Overall Headshots
    sqliteConnection = sqlite3.connect('valAnalyzer.db')
    cursor = sqliteConnection.cursor()

    query = """SELECT headshots FROM Scoreboards WHERE name = ?"""
    cursor.execute(query, (name,))

    match_list = cursor.fetchall()
    total_hs = 0
    for match in match_list:
        total_hs += match[0]

    return total_hs

def get_overall_bodyshots(name): # Gets Overall Bodyshots
    sqliteConnection = sqlite3.connect('valAnalyzer.db')
    cursor = sqliteConnection.cursor()

    query = """SELECT headshots FROM Scoreboards WHERE name = ?"""
    cursor.execute(query, (name,))

    match_list = cursor.fetchall()
    total_bs = 0
    for match in match_list:
        total_bs += match[0]

    return total_bs

def get_overall_legshots(name): # Gets Overall Legshots
    sqliteConnection = sqlite3.connect('valAnalyzer.db')
    cursor = sqliteConnection.cursor()

    query = """SELECT headshots FROM Scoreboards WHERE name = ?"""
    cursor.execute(query, (name,))

    match_list = cursor.fetchall()
    total_ls = 0
    for match in match_list:
        total_ls += match[0]

    return total_ls

def get_overall_hs_rate(name): # Gets Overall Headshot Rate
    headshots = get_overall_headshots(name)
    bodyshots = get_overall_bodyshots(name)
    legshots = get_overall_legshots(name)

    return headshots / (headshots + bodyshots + legshots)

def get_overall_bs_rate(name): # Gets Overall Bodyshot Rate
    headshots = get_overall_headshots(name)
    bodyshots = get_overall_bodyshots(name)
    legshots = get_overall_legshots(name)

    return bodyshots / (headshots + bodyshots + legshots)

def get_overall_ls_rate(name): # Gets Overall Legshot Rate
    headshots = get_overall_headshots(name)
    bodyshots = get_overall_bodyshots(name)
    legshots = get_overall_legshots(name)

    return legshots / (headshots + bodyshots + legshots)

def get_overall_ACS(name): # Gets Overall Average Combat Score
    sqliteConnection = sqlite3.connect('valAnalyzer.db')
    cursor = sqliteConnection.cursor()

    query = """SELECT score FROM Scoreboards WHERE name = ?"""
    cursor.execute(query, (name,))

    match_list = cursor.fetchall()
    total_score = 0
    for match in match_list:
        total_score += match[0]

    rounds = get_overall_rounds_played(name)

    return total_score / rounds

def get_overall_KPR(name): # Gets Overall Kills Per Round
    kills = get_overall_kills(name)
    rounds = get_overall_rounds_played(name)

    return kills / rounds

def get_player_matches(name): # Returns False if user is not in DB, returns [Match ID, Start Time, Game Length, Red Score, Blue Score] in 2D Array if in DB
    sqliteConnection = sqlite3.connect('valAnalyzer.db')
    cursor = sqliteConnection.cursor()

    query = """SELECT match_id FROM Scoreboards WHERE name = ?"""
    cursor.execute(query, (name,))

    match_ids = cursor.fetchall()
    if len(match_ids) == 0:
        return False
    else:
        query = """SELECT match_id, map, start_time, game_length, red_score, blue_score FROM MatchInfo WHERE match_id = ? """
        for i in range(len(match_ids) - 1):
           query += """OR match_id = ? """
        cursor.execute(query, tuple(i[0] for i in match_ids))
        data = cursor.fetchall()
        return [list(i) for i in data]

def get_player_match_info(name, match_info): #Returns Agent, Scoreboard Place, Kills, Deaths, Assists, Ally Score, Enemy Score, Results, Start Time, Map
    sqliteConnection = sqlite3.connect('valAnalyzer.db')
    cursor = sqliteConnection.cursor()

    query = """SELECT name, agent, team, score, kills, deaths, assists FROM Scoreboards WHERE match_id = ?"""
    cursor.execute(query, (match_info[0],))

    match_scoreboard = sorted([list(i) for i in cursor.fetchall()], key=lambda x: x[3], reverse=True)

    agent = ""
    scoreboard_place = 1
    for player in match_scoreboard:
        if player[0] == name:
            agent = "frontend/src/agent_icons/" + player[1] + "_icon.webp"
            team = player[2]
            kills = player[4]
            deaths = player[5]
            assists = player[6]
            break
        scoreboard_place += 1
    match scoreboard_place:
        case 1:
            scoreboard_place = "MVP"
        case 2:
            scoreboard_place = "2nd"
        case 3:
            scoreboard_place = "3rd"
        case _:
            scoreboard_place = str(scoreboard_place) + "th"
    
    ally_score = 0
    enemy_score = 0
    if team == "Red":
        ally_score = match_info[4]
        enemy_score = match_info[5]
    else:
        ally_score = match_info[5]
        enemy_score = match_info[4]
    
    results = ""
    if ally_score > enemy_score:
        results = "VICTORY"
    elif enemy_score > ally_score:
        results = "DEFEAT"
    else:
        results = "DRAW"
    
    return [agent, scoreboard_place, kills, deaths, assists, ally_score, enemy_score, results, match_info[2], match_info[1]]

def convert_image_to_base64(path): # Converts Image to Base64 URL
    file = open(path, "rb")
    contents = file.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    file.close()

    return "data:image/gif;base64," + data_url

def main():
    create_databases()

if __name__ == "__main__":
    main()