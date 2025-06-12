import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.models import Playlist, SpotifyAccount
from backend.api.serializers import PlaylistSerializer
from backend.utils import spotify_helpers as sh

from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.authentication import SessionAuthentication

from django.shortcuts import redirect

log = logging.getLogger(__name__)


class SessionTokenView(APIView):
    """
    API view that generates a new access token for the authenticated user using session authentication.

    Authentication:
        - Requires the user to be authenticated via session.

    Methods:
        get(request):
            Generates a JWT access token for the current user with a 2-hour expiration time.
            Returns:
                Response containing the access token as a string in the "access" field.
    """

    authentication_classes = [SessionAuthentication]
    permission_classes     = [permissions.IsAuthenticated]

    def get(self, request):
        token = AccessToken.for_user(request.user)
        token.set_exp(lifetime=timedelta(hours=2))
        return Response({"access": str(token)})

class SpotifyLoginView(APIView):
    """
    APIView that provides the Spotify consent (authorization) URL for authenticated users.

    GET:
        Returns a JSON response containing the Spotify authorization URL for the logged-in user.
        The user can use this URL to authorize the application with their Spotify account.

    Permissions:
        - Requires the user to be authenticated.
    """
    """Return the Spotify consent URL for the logged-in user."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        oauth = sh.get_spotify_oauth()
        return Response({"url": oauth.get_authorize_url()})


class SpotifyCallbackView(APIView):
    """
    View to handle Spotify OAuth callback.

    This view processes the authorization code returned by Spotify after the user grants access.
    It exchanges the code for access and refresh tokens, retrieves the user's Spotify profile,
    and updates or creates a SpotifyAccount associated with the authenticated user.

    Methods:
        get(request):
            Handles GET requests with a 'code' query parameter.
            - Exchanges the code for tokens.
            - Retrieves the user's Spotify profile.
            - Updates or creates the SpotifyAccount for the user.
            - Returns a success response or an error message.

    Permissions:
        Requires the user to be authenticated.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        code = request.query_params.get("code")
        if not code:
            return Response({"detail": "Missing ?code"}, status=400)

        try:
            token_data = sh.exchange_code(code)
            profile = sh.get_profile(token_data["access_token"])
        except Exception as exc:
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
        return redirect("/spotify-playlists/")

class PlaylistViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user playlists.

    Endpoints:
        /api/playlists/  - Provides CRUD operations for playlists.

    Key Behaviors:
        - Only authenticated users can access these endpoints.
        - Queryset is limited to playlists owned by the requesting user, ordered by creation date (descending).
        - On creation (POST):
            1. Saves the playlist record to the database.
            2. Ensures a valid Spotify client for the user.
            3. Creates a new Spotify playlist and adds recommended tracks based on the mood prompt.
            4. Updates the playlist record with the generated Spotify playlist ID.

    Notes:
        - All operations are performed synchronously (no background tasks).
        - Exceptions during Spotify operations are logged and propagated.
    /api/playlists/  - CRUD for playlists.
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

        sp = sh.make_client(self.request.user)

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
        except Exception as exc:
            log.exception("Playlist generation failed")
            raise

        playlist.spotify_id = spotify_id
        playlist.save(update_fields=["spotify_id"])
