from django.db import models

class GameInfo(models.Model):
  matchid = models.CharField(max_length=255, primary_key=True)    #primary key
  map = models.CharField(max_length=255)
  time_start = models.CharField(max_length=255)
  game_length = models.CharField(max_length=255)
  result = models.CharField(max_length=255)
  score = models.CharField(max_length=255)

class GameStats(models.Model):
  matchid = models.ForeignKey(GameInfo, primary_key=True, on_delete=models.CASCADE)            #foreign key
  team = models.CharField(max_length=255)
  character = models.CharField(max_length=255)
  name = models.CharField(max_length=255)
  acs = models.IntegerField(default=0)
  kills = models.IntegerField(default=0)
  deaths = models.IntegerField(default=0)
  assists = models.IntegerField(default=0)
  first_bloods = models.IntegerField(default=0)
  first_deaths = models.IntegerField(default=0)
  plants = models.IntegerField(default=0)
  defuses = models.IntegerField(default=0)
  headshots = models.IntegerField(default=0)
  bodyshots = models.IntegerField(default=0)
  legshots = models.IntegerField(default=0)
  hs_rate = models.IntegerField(default=0)
  c_uses = models.IntegerField(default=0)
  q_uses = models.IntegerField(default=0)
  e_uses = models.IntegerField(default=0)
  x_uses = models.IntegerField(default=0)
  ultimate_kills = models.IntegerField(default=0)

class GameTimeline(models.Model):
  matchid= models.ForeignKey(GameInfo, primary_key=True, on_delete=models.CASCADE)                 #foreign key
  round = models.IntegerField(default=0)                                          #foreign key
  winning_team = models.CharField(max_length=255)   
  end_type = models.CharField(max_length=255)

class GameRounds(models.Model):
  matchid = models.ForeignKey(GameInfo, primary_key=True, on_delete=models.CASCADE)                    #foreign key
  round = models.IntegerField(default=0)                                                      #composite key
  time_ms = models.IntegerField(default=0)                                                    #composite key
  time = models.CharField(max_length=255)
  event_type = models.CharField(max_length=255)
  performer = models.CharField(max_length=255)
  site = models.CharField(max_length=255)
  weapon = models.CharField(max_length=255)
  victim = models.CharField(max_length=255)
  victim_death_loc_x = models.IntegerField(default=0)
  victim_death_loc_y = models.IntegerField(default=0)
  
class GamePlayerInfo(models.Model):
  matchid = models.ForeignKey(GameInfo, primary_key=True, on_delete=models.CASCADE)              #foreign composite key
  round = models.IntegerField(default=0)                       #foreign composite key
  time_ms = models.IntegerField(default=0)                     #foreign composite key
  player_name = models.CharField(max_length=255)
  player_team = models.CharField(max_length=255)
  player_loc_x = models.IntegerField(default=0)
  player_loc_y = models.IntegerField(default=0)
  player_loc_angle = models.FloatField(default=0)