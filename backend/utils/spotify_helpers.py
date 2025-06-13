from __future__ import annotations

import os
import random
from datetime import timedelta
from typing import List

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.utils import timezone
from backend.models import SpotifyAccount

from dotenv import load_dotenv
load_dotenv()

def get_spotify_oauth() -> SpotifyOAuth:
    """
    Creates and returns a SpotifyOAuth object configured with client credentials and redirect URI from environment variables.

    Returns:
        SpotifyOAuth: An instance of SpotifyOAuth initialized with the client ID, client secret, redirect URI, and scopes for modifying playlists.

    Environment Variables:
        SPOTIFY_CLIENT_ID: The Spotify application's client ID.
        SPOTIFY_CLIENT_SECRET: The Spotify application's client secret.
        SPOTIFY_REDIRECT_URI: The redirect URI registered with the Spotify application.
    """
    return SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope="playlist-modify-public playlist-modify-private",
        cache_handler=None,
        show_dialog=True,
    )


def exchange_code(code: str) -> dict:
    """
    Exchanges an authorization code for an access token using the Spotify OAuth flow.

    Args:
        code (str): The authorization code received from Spotify after user authentication.

    Returns:
        dict: A dictionary containing the access token and related information.

    Raises:
        spotipy.oauth2.SpotifyOauthError: If the token exchange fails.
    """
    oauth = get_spotify_oauth()
    return oauth.get_access_token(code, as_dict=True)  # spotipy ≥2.23


def refresh_spotify_token(sp_account: SpotifyAccount) -> None:
    """
    Refreshes the Spotify access token for the given SpotifyAccount instance if the current token is about to expire.

    Args:
        sp_account (SpotifyAccount): The Spotify account instance whose access token needs to be refreshed.

    Returns:
        None

    Notes:
        - If the current access token is valid for more than 60 seconds, the function returns without refreshing.
        - Otherwise, it uses the stored refresh token to obtain a new access token and updates the account instance.
    """
    if sp_account.token_expires_at - timezone.now() > timedelta(seconds=60):
        return  # still valid

    oauth = get_spotify_oauth()
    token_data = oauth.refresh_access_token(sp_account.refresh_token)  # :contentReference[oaicite:0]{index=0}

    sp_account.access_token = token_data["access_token"]
    sp_account.token_expires_at = timezone.now() + timedelta(
        seconds=token_data["expires_in"]
    )
    sp_account.save(update_fields=["access_token", "token_expires_at"])


def make_client(user) -> spotipy.Spotify:
    """
    Creates and returns a Spotipy client instance for the given user.

    This function retrieves or creates a SpotifyAccount associated with the user.
    If the user has not connected their Spotify account (i.e., no access token is present),
    a RuntimeError is raised. The function ensures the access token is refreshed if needed,
    and then returns an authenticated Spotipy client.

    Args:
        user: The user object for whom the Spotify client is to be created.

    Returns:
        spotipy.Spotify: An authenticated Spotipy client instance.

    Raises:
        RuntimeError: If the user has not connected their Spotify account.
    """
    sp_account, _ = SpotifyAccount.objects.get_or_create(
        user=user,
        defaults=dict(
            spotify_id   = "",
            access_token = "",
            refresh_token= "",
            token_expires_at = timezone.now() - timedelta(days=1),
        ),
    )

    if not sp_account.access_token:
        raise RuntimeError("User has not connected Spotify yet.")

    refresh_spotify_token(sp_account)
    return spotipy.Spotify(auth=sp_account.access_token)


def create_playlist(sp: spotipy.Spotify, owner_id: str, name: str, description: str) -> str:
    """
    Creates a new private Spotify playlist for the specified user.

    Args:
        sp (spotipy.Spotify): An authenticated Spotipy client instance.
        owner_id (str): The Spotify user ID of the playlist owner.
        name (str): The name of the new playlist.
        description (str): The description for the playlist (will be truncated to 300 characters).

    Returns:
        str: The ID of the newly created playlist.
    """
    playlist = sp.user_playlist_create(
        owner_id,
        name,
        public=False,
        description=description[:300],
    )
    return playlist["id"]


def add_tracks(sp: spotipy.Spotify, playlist_id: str, track_uris: List[str]) -> None:
    """
    Adds a list of tracks to a Spotify playlist in batches of 100.

    Args:
        sp (spotipy.Spotify): An authenticated Spotipy client instance.
        playlist_id (str): The Spotify ID of the playlist to add tracks to.
        track_uris (List[str]): A list of Spotify track URIs to add to the playlist.

    Returns:
        None
    """
    for i in range(0, len(track_uris), 100):
        sp.playlist_add_items(playlist_id, track_uris[i : i + 100])


GENERIC_SEEDS = ["pop", "rock", "indie", "electronic", "hip-hop"]  # fallback


def generate_recommendations(sp: spotipy.Spotify, prompt: str, size: int = 30) -> List[str]:
    """
    Generate a list of Spotify track URIs based on a search prompt and recommended tracks.

    This function first searches for tracks matching the given prompt and collects their URIs.
    If the number of found tracks is less than the requested size, it fills the remainder
    by generating recommendations using generic genre seeds.

    Args:
        sp (spotipy.Spotify): An authenticated Spotipy client instance.
        prompt (str): The search query to find relevant tracks.
        size (int, optional): The total number of track URIs to return. Defaults to 30.

    Returns:
        List[str]: A list of Spotify track URIs, up to the specified size.
    """
    uris: list[str] = []

    search_results = sp.search(q=prompt, type="track", limit=size)["tracks"]["items"]
    uris.extend([t["uri"] for t in search_results])

    remaining = size - len(uris)
    if remaining > 0:
        seeds = random.sample(GENERIC_SEEDS, k=min(5, len(GENERIC_SEEDS)))
        recs = sp.recommendations(seed_genres=seeds, limit=remaining)
        uris.extend([t["uri"] for t in recs["tracks"]])

    return uris[:size]


def get_profile(access_token: str) -> dict:
    """
    Fetches the Spotify profile information of the current user using the provided access token.

    Args:
        access_token (str): A valid Spotify access token.

    Returns:
        dict: A dictionary containing the current user's Spotify profile information.

    Raises:
        spotipy.SpotifyException: If the access token is invalid or expired.
    """
    """Return current_user profile from a raw token (used in callback)."""
    sp = spotipy.Spotify(auth=access_token)
    return sp.current_user()
