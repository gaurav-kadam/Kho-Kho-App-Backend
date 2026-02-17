from django.urls import path
from .views import OfficialListAPI,CreateOfficialAPI

urlpatterns = [
    path("officials/", OfficialListAPI.as_view()),
    path("create-official/", CreateOfficialAPI.as_view()),
]
