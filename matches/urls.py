from django.urls import path
from .views import (
    StartMatchAPI,
    EndMatchAPI,
    MatchStateAPI,
    PauseMatchAPI,
    ResumeMatchAPI,
    LiveMatchAPI,
    AssignOfficialAPI,
    AssignMatchPlayerAPI
)
urlpatterns = [
    path("start/<int:match_id>/", StartMatchAPI.as_view()),
    path("pause/<int:match_id>/", PauseMatchAPI.as_view()),
    path("resume/<int:match_id>/", ResumeMatchAPI.as_view()),
    path("end/<int:match_id>/", EndMatchAPI.as_view()),
    path("state/<int:match_id>/", MatchStateAPI.as_view()),
    path("live/<int:match_id>/", LiveMatchAPI.as_view()),
    path("assign-official/", AssignOfficialAPI.as_view()),
    path("assign-player/", AssignMatchPlayerAPI.as_view()),


]

