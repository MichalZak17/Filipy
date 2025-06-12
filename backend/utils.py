import os
import requests
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import JsonResponse

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.conf import settings


from dotenv import load_dotenv

from backend.models import Spotify

load_dotenv()

def generate_track_uris(sp, seed_artists, seed_genres, seed_tracks, size=50):
    rec = sp.recommendations(seed_artists=seed_artists,
                             seed_genres=seed_genres,
                             seed_tracks=seed_tracks,
                             limit=size)
    return [t["uri"] for t in rec["tracks"]]


def make_client(user):
    return spotipy.Spotify(auth=user.spotify_access_token)

def create_playlist(user, name, description):
    sp = make_client(user)
    playlist = sp.user_playlist_create(
        user.spotify_id, name, public=False, description=description
    )  # creates and returns snapshot_id
    return playlist["id"]

def add_tracks(user, playlist_id, track_uris):
    sp = make_client(user)
    # Spotify caps at 100 URIs per call
    for i in range(0, len(track_uris), 100):
        sp.playlist_add_items(playlist_id, track_uris[i:i+100])


def get_spotify_access_token(user: User):
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        raise ValueError("Spotify client ID and secret must be set in environment variables.")
    
    token_url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(token_url, data=data, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to get access token: {response.text}")
    
    token_data = response.json()
    access_token = token_data.get("access_token")
    token_type = token_data.get("token_type", "Bearer")
    expires_in = token_data.get("expires_in", 3600)

    spotify_profile, created = Spotify.objects.get_or_create(user=user)
    spotify_profile.access_token = access_token
    spotify_profile.token_type = token_type
    spotify_profile.expires_at = timezone.now() + timezone.timedelta(seconds=expires_in)
    spotify_profile.save()
    return access_token, token_type, spotify_profile.expires_at