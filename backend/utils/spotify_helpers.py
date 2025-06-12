"""
Thin helpers around Spotipy + minimal prompt→track logic.
All low-level Spotify calls live here so views.py stays clean.
"""
from __future__ import annotations

import os
import random
from datetime import timedelta
from typing import List

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.conf import settings
from django.utils import timezone
from backend.models import SpotifyAccount

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

# --------------------------------------------------------------------------- #
# 1.  OAuth helpers
# --------------------------------------------------------------------------- #
def get_spotify_oauth() -> SpotifyOAuth:
    """Build a reusable SpotifyOAuth object (no cache file)."""
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
    Convert the ?code from /authorize to tokens.
    Returns a dict with access_token / refresh_token / expires_in.
    """
    oauth = get_spotify_oauth()
    return oauth.get_access_token(code, as_dict=True)  # spotipy ≥2.23


def refresh_spotify_token(sp_account: SpotifyAccount) -> None:
    """
    Refresh `sp_account.access_token` in-place if it expires in <60 s.
    Called automatically by make_client().
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
    Return a Spotipy client for `user`.
    If the user hasn't linked a SpotifyAccount yet,
    create an empty placeholder so later steps can update it.
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

    # if no tokens yet, raise an explicit error instead of AttributeError
    if not sp_account.access_token:
        raise RuntimeError("User has not connected Spotify yet.")

    refresh_spotify_token(sp_account)
    return spotipy.Spotify(auth=sp_account.access_token)


# --------------------------------------------------------------------------- #
# 2.  Playlist helpers
# --------------------------------------------------------------------------- #
def create_playlist(
    sp: spotipy.Spotify, owner_id: str, name: str, description: str
) -> str:
    """
    Create a private playlist and return its Spotify ID.
    """
    playlist = sp.user_playlist_create(
        owner_id,
        name,
        public=False,
        description=description[:300],
    )
    return playlist["id"]


def add_tracks(sp: spotipy.Spotify, playlist_id: str, track_uris: List[str]) -> None:
    """Chunk-add tracks (Spotify hard-limit: 100 per request)."""
    for i in range(0, len(track_uris), 100):
        sp.playlist_add_items(playlist_id, track_uris[i : i + 100])


# --------------------------------------------------------------------------- #
# 3.  Very simple prompt → recommendations demo
# --------------------------------------------------------------------------- #
GENERIC_SEEDS = ["pop", "rock", "indie", "electronic", "hip-hop"]  # fallback


def generate_recommendations(
    sp: spotipy.Spotify, prompt: str, size: int = 30
) -> List[str]:
    """
    **Naïve baseline**:
      • Try `search` for top tracks matching the prompt words.
      • If <size results, pad using recommendations endpoint & generic seeds.
    Improve/replace with real mood/NLP pipeline whenever you like.
    """
    uris: list[str] = []

    # --- 1) keyword search -------------------------------------------------- #
    search_results = sp.search(q=prompt, type="track", limit=size)["tracks"]["items"]
    uris.extend([t["uri"] for t in search_results])

    # --- 2) top-up with recommendations ------------------------------------ #
    remaining = size - len(uris)
    if remaining > 0:
        seeds = random.sample(GENERIC_SEEDS, k=min(5, len(GENERIC_SEEDS)))
        recs = sp.recommendations(
            seed_genres=seeds, limit=remaining
        )  # :contentReference[oaicite:1]{index=1}
        uris.extend([t["uri"] for t in recs["tracks"]])

    return uris[:size]


# --------------------------------------------------------------------------- #
# 4.  Convenience
# --------------------------------------------------------------------------- #
def get_profile(access_token: str) -> dict:
    """Return current_user profile from a raw token (used in callback)."""
    sp = spotipy.Spotify(auth=access_token)
    return sp.current_user()
