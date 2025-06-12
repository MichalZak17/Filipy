"""
REST endpoints for Filipy (Spotify mood-based playlist generator).
Relies on helper functions in backend/utils/spotify_helpers.py
"""
import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.models import Playlist, SpotifyAccount
from backend.api.serializers import PlaylistSerializer
from backend.utils import spotify_helpers as sh


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework_simplejwt.tokens import AccessToken

log = logging.getLogger(__name__)


from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.views import APIView
from rest_framework import permissions
from django.utils import timezone
from datetime import timedelta

class SessionTokenView(APIView):
    authentication_classes = [SessionAuthentication]          # ←  add this
    permission_classes     = [permissions.IsAuthenticated]

    def get(self, request):
        token = AccessToken.for_user(request.user)
        token.set_exp(lifetime=timedelta(hours=2))            # short-lived
        return Response({"access": str(token)})

# ---------- AUTH FLOW ---------- #
class SpotifyLoginView(APIView):
    """Return the Spotify consent URL for the logged-in user."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        oauth = sh.get_spotify_oauth()
        return Response({"url": oauth.get_authorize_url()})


class SpotifyCallbackView(APIView):
    """
    Handles ?code=... returned by Spotify after the user grants access.
    Stores / updates SpotifyAccount and redirects front-end if needed.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        code = request.query_params.get("code")
        if not code:
            return Response({"detail": "Missing ?code"}, status=400)

        try:
            token_data = sh.exchange_code(code)
            profile = sh.get_profile(token_data["access_token"])
        except Exception as exc:  # pragma: no cover
            log.exception("Spotify callback failed")
            return Response({"detail": str(exc)}, status=500)

        SpotifyAccount.objects.update_or_create(
            user=request.user,
            defaults=dict(
                spotify_id=profile["id"],
                access_token=token_data["access_token"],
                refresh_token=token_data["refresh_token"],
                token_expires_at=timezone.now()
                + timedelta(seconds=token_data["expires_in"]),
            ),
        )
        return Response({"detail": "Spotify connected"})


# ---------- PLAYLIST CRUD ---------- #
class PlaylistViewSet(viewsets.ModelViewSet):
    """
    /api/playlists/  – CRUD for playlists.
    POST performs all heavy lifting synchronously (no Celery).
    """

    serializer_class = PlaylistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Playlist.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        """
        1. Save DB record.
        2. Make / refresh Spotify client.
        3. Create playlist + add tracks.
        4. Update spotify_id on the model.
        """
        playlist: Playlist = serializer.save(user=self.request.user)

        # ---------- Step 2: ensure valid token ---------- #
        sp = sh.make_client(self.request.user)

        # ---------- Step 3: create playlist + tracks ---------- #
        try:
            spotify_id = sh.create_playlist(
                sp=sp,
                owner_id=self.request.user.spotifyaccount.spotify_id,
                name=playlist.name,
                description=playlist.description or playlist.mood_prompt,
            )
            tracks = sh.generate_recommendations(
                sp=sp, prompt=playlist.mood_prompt, size=30
            )
            if tracks:
                sh.add_tracks(sp, spotify_id, tracks)
        except Exception as exc:  # pragma: no cover
            log.exception("Playlist generation failed")
            raise

        # ---------- Step 4: save back to DB ---------- #
        playlist.spotify_id = spotify_id
        playlist.save(update_fields=["spotify_id"])
