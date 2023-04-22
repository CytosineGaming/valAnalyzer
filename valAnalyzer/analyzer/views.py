from django.http import HttpResponse
from django.template import loader
from analyzer.models import GameInfo
from analyzer.valAnalyzer import get_match_history_info
import analyzer.database as db
import logging

logger = logging.getLogger(__name__)
logger.info("wauw")

def analyzer(request):
  all_games = GameInfo.objects.all().values()
  recent_games = get_match_history_info("na", "HKR Cytosine", "7670", 10, "custom")
  template = loader.get_template('main.html')
  context = {
    'all_games': all_games,
    'recent_games': recent_games
  }
  return HttpResponse(template.render(context, request))

def upload_game(request):
  template = loader.get_template('main.html')
  all_games = GameInfo.objects.all().values()
  recent_games = get_match_history_info("na", "HKR Cytosine", "7670", 10, "custom")

  if request.method == "POST":
    match_id = request.POST.get('matchID')
    name = request.POST.get('name')
    tag = request.POST.get('tag')
    db.upload_match(match_id, name, tag)
  context = {
    'all_games': all_games,
    'recent_games': recent_games
  }
  return HttpResponse(template.render(context, request))