from rest_framework import serializers
from backend.models import Playlist

class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Playlist
        fields = ("id", "name", "description", "mood_prompt",
                  "spotify_id", "created_at")
        read_only_fields = ("spotify_id", "created_at")
