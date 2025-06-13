from rest_framework import serializers
from backend.models import Playlist

class PlaylistSerializer(serializers.ModelSerializer):
    """
    Serializer for the Playlist model.

    Serializes the following fields:
        - id: Unique identifier for the playlist.
        - name: Name of the playlist.
        - description: Description of the playlist.
        - mood_prompt: Mood or prompt associated with the playlist.
        - spotify_id: Spotify identifier for the playlist (read-only).
        - created_at: Timestamp when the playlist was created (read-only).
    """
    class Meta:
        model  = Playlist
        fields = ("id", "name", "description", "mood_prompt",
                  "spotify_id", "created_at")
        read_only_fields = ("spotify_id", "created_at")
