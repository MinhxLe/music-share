from enum import StrEnum
import settings
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth


# https://developer.spotify.com/documentation/web-api/concepts/scopes
class Scope(StrEnum):
    USER_LIBRARY_READ = "user-library-read"
    USER_READ_RECENTLY_PLAYED = "user-read-recently-played"
    USER_TOP_READ = "user-top-read"
    USER_READ_PRIVATE = "user-read-private"
    USER_READ_EMAIL = "user-read-email"
    PLAYLIST_READ_PRIVATE = "playlist-read-private"
    PLAYLIST_READ_COLLABORATIVE = "playlist-read-collaborative"
    PLAYLIST_MODIFY_PRIVATE = "playlist-modify-private"
    PLAYLIST_MODIFY_PUBLIC = "playlist-modify-public"


def _get_client():
    return Spotify(
        auth_manager=SpotifyOAuth(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
            redirect_uri=settings.SPOTIFY_REDIRECT_URI,
            scope=[s for s in Scope],
        )
    )


sp = _get_client()
sp.user_playlists
