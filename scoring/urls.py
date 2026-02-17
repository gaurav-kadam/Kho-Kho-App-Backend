from django.urls import path
from .views import CreateScoreEventAPI, MatchScoreboardAPI

urlpatterns = [
    path('create-score/', CreateScoreEventAPI.as_view()),
    path('scoreboard/<int:match_id>/', MatchScoreboardAPI.as_view()),
]
