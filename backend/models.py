from django.db import models
from django.conf import settings


class Spotify(models.Model):
    """
    Model representing a Spotify user authentication profile.

    Fields:
        user (OneToOneField): Link to Django user.
        access_token (CharField): Spotify API access token.
        refresh_token (CharField): Spotify API refresh token.
        token_type (CharField): Type of token (default: Bearer).
        expires_at (DateTimeField): When the access token expires.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="spotify_profile",
    )
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    token_type = models.CharField(max_length=50, default="Bearer")
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Spotify profile for {self.user.username}"
