from django.urls import path
from . import views

urlpatterns = [
    path('analyzer/', views.analyzer, name='analyzer'),
    path('upload_game/', views.upload_game, name='upload_game')
]