from .views import *
from django.urls import path

urlpatterns = [
    path("", index_view, name="index"),
    path("home/", index_view, name="home"),
    path("login/", login_view, name="login"),
    path("forgotten-password/", forgotten_password_view, name="forgotten_password"),
    path("logout/", logout_view, name="logout"),
    path("spotify-playlists/", spotify_playlists, name="spotify_playlists"),
    path("settings/", settings_view, name="settings"),
    path("signup/", signup_view, name="signup"),
]
