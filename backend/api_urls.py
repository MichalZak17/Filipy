from django.urls import path, include
from rest_framework.routers import DefaultRouter
from backend.api.views import (
    PlaylistViewSet,
    SpotifyLoginView,
    SpotifyCallbackView,
    SessionTokenView,          # ← the bridge view
)

router = DefaultRouter()
router.register(r"playlists", PlaylistViewSet, basename="playlist")

urlpatterns = [
    # put the explicit routes **before** the router include
    path('token/session/', SessionTokenView.as_view(), name='jwt_from_session'),
    path('auth/spotify/login/',    SpotifyLoginView.as_view()),
    path('auth/spotify/callback/', SpotifyCallbackView.as_view()),

    path('', include(router.urls)),
]