from django.db import models
from django.conf import settings


class SpotifyAccount(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    spotify_id = models.CharField(max_length=120)
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_expires_at = models.DateTimeField()


class Playlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    mood_prompt = models.CharField(max_length=240)
    spotify_id = models.CharField(max_length=120, blank=True)  # filled later
    created_at = models.DateTimeField(auto_now_add=True)
