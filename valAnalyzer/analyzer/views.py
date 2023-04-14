from django.http import HttpResponse
from django.template import loader
from analyzer.models import GameInfo
from analyzer.valAnalyzer import get_match_history_info

def analyzer(request):
  all_games = GameInfo.objects.all().values()
  recent_games = get_match_history_info("na", "HKR Cytosine", "7670", 10, "custom")
  template = loader.get_template('bitch.html')
  context = {
    'all_games': all_games,
    'recent_games': recent_games
  }
  return HttpResponse(template.render())