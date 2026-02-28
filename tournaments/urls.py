from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TournamentViewSet, tournament_standings

router = DefaultRouter()
router.register(r'tournaments', TournamentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('tournaments/<int:tournament_id>/standings/', tournament_standings, name='tournament-standings'),
]