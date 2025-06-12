from django.contrib import admin
from .models import SpotifyAccount, Playlist


@admin.register(SpotifyAccount)
class SpotifyAccountAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SpotifyAccount._meta.fields]
    search_fields = ["spotify_id", "user__username"]
    list_filter = ["token_expires_at"]


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Playlist._meta.fields]
    search_fields = ["name", "description", "mood_prompt", "user__username"]
    list_filter = ["created_at", "user"]
