import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST  # enforce verb ✋
from django.contrib.auth.decorators import login_required  # gate to logged-in users
from django.views.decorators.csrf import csrf_exempt  # optional for API
from django.utils import timezone

from .utils import (  # rename your helper file as you wish
    create_playlist,
    add_tracks,
    generate_track_uris,
    make_client,
    get_spotify_access_token,
)

# ---------- helpers ---------- #


def _json_request_body(request):
    try:
        return json.loads(request.body.decode())
    except (ValueError, UnicodeDecodeError):
        return None


def _bad_request(msg):
    return HttpResponseBadRequest(json.dumps({"error": msg}), content_type="application/json")


# ---------- views ---------- #


@login_required  # <-- redirect if not logged in :contentReference[oaicite:2]{index=2}
@require_POST  # <-- only POST allowed :contentReference[oaicite:3]{index=3}
def create_playlist_view(request):
    """POST  {name, description?}  →  {playlist_id}"""
    body = _json_request_body(request)
    if not body or "name" not in body:
        return _bad_request("Missing field ‘name’")
    playlist_id = create_playlist(request.user, body["name"], body.get("description", ""))
    return JsonResponse({"playlist_id": playlist_id})


@login_required
@require_POST
def add_tracks_view(request):
    """POST  {playlist_id, uris:[…]}  →  {added: n}"""
    body = _json_request_body(request)
    if not body or {"playlist_id", "uris"} - body.keys():
        return _bad_request("Fields ‘playlist_id’ and ‘uris’ are required")
    add_tracks(request.user, body["playlist_id"], body["uris"])
    return JsonResponse({"added": len(body["uris"])})


@login_required
@require_POST
def generate_playlist_view(request):
    """
    POST  {
        name, description?,
        seed_artists?, seed_genres?, seed_tracks?,
        size?=50
    } →  {playlist_id, track_count}
    """
    body = _json_request_body(request)
    if not body or "name" not in body:
        return _bad_request("Missing field ‘name’")

    # ensure we have a fresh token before long-running ops
    expires_at = request.user.spotify.expires_at
    if not expires_at or expires_at <= timezone.now():
        get_spotify_access_token(request.user)  # refresh silently

    sp = make_client(request.user)
    # 1️⃣ build /recommendations query (Spotify allows ≤ 5 seeds total) :contentReference[oaicite:4]{index=4}
    uris = generate_track_uris(
        sp,
        body.get("seed_artists", []),
        body.get("seed_genres", []),
        body.get("seed_tracks", []),
        size=body.get("size", 50),
    )
    # 2️⃣ create playlist and push tracks
    playlist_id = create_playlist(request.user, body["name"], body.get("description", ""))
    add_tracks(
        request.user, playlist_id, uris
    )  # uses /playlists/{id}/tracks :contentReference[oaicite:5]{index=5}
    return JsonResponse({"playlist_id": playlist_id, "track_count": len(uris)})


# (optional) public health-check
def ping(request):
    return JsonResponse({"pong": True, "time": timezone.now().isoformat()})
