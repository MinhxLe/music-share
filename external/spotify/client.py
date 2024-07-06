from collections.abc import Callable
from datetime import datetime
from enum import StrEnum
from typing import Any, ClassVar, List, Literal, LiteralString

from requests.auth import HTTPBasicAuth
from requests.utils import parse_dict_header
from spotipy.cache_handler import json
import settings
from pydantic import BaseModel, Extra, validator
from requests_oauthlib import OAuth2Session


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


BASE_URL = "https://accounts.spotify.com"
AUTH_URL = f"{BASE_URL}/authorize"
TOKEN_URL = f"{BASE_URL}/api/token"

BASE_API_URL = "https://api.spotify.com/v1"


class Token(BaseModel, extra=Extra.ignore):
    access_token: str
    refresh_token: str
    expires_in: int
    scope: list[str]
    expires_at: datetime

    @validator("expires_at", pre=True)
    def parse_expires_at(cls, value):
        if isinstance(value, (float, int)):
            return datetime.fromtimestamp(value)
        return value

    def serialize_timestamp(self) -> dict:
        data = self.dict()
        if self.expires_at:
            data["expires_at"] = self.expires_at.timestamp()
        return data


class AuthRequest(BaseModel):
    url: str
    state: str


class Image(BaseModel):
    url: str
    height: int | None
    width: int | None


class ExternalUrlSet(BaseModel):
    spotify: str


class SpotifyBaseModel(BaseModel, extra=Extra.ignore):
    id: str
    href: str
    external_urls: ExternalUrlSet
    _type: ClassVar[str] = "unspecified"

    @property
    def uri(self):
        return f"spotify:{self._type}:{self.id}"

    @classmethod
    def get_uri(cls, id: str) -> str:
        return f"spotify:{cls._type}:{id}"

    class Config:
        arbitrary_types_allowed = True


class User(SpotifyBaseModel):
    _type = "user"
    id: str
    display_name: str
    email: str
    images: list[Image]


class EmbeddedArtist(SpotifyBaseModel):
    _type = "artist"


class Artist(EmbeddedArtist):
    name: str
    genres: list[str]
    images: list[Image]


class EmbeddedAlbum(SpotifyBaseModel):
    _type = "album"


class Album(EmbeddedAlbum):
    name: str
    images: list[Image]
    artists: list[EmbeddedArtist]
    genres: list[str]


class Track(SpotifyBaseModel):
    _type = "track"
    album: EmbeddedAlbum
    artists: list[EmbeddedArtist]
    duration_ms: int
    href: str
    name: str
    popularity: int
    preview_url: str | None


class RecentlyPlayedTrack(BaseModel):
    track: Track
    played_at: datetime


class PlaylistTrack(BaseModel):
    added_at: datetime | None
    track: Track


class PaginatedResponse[T](BaseModel, extra=Extra.ignore):
    limit: int
    next: str | None
    items: list[T]


class UserPlaylist(SpotifyBaseModel):
    _type = "playlist"
    collaborative: bool
    description: str | None
    name: str
    public: bool | None
    snapshot_id: str


class Session(OAuth2Session):
    def __init__(
        self,
        save_token_fn: Callable[[Token], None] = lambda _: None,
        token: Token | None = None,
    ):
        serialized_token = token.model_dump(mode="json") if token else None

        def save_token_fn_wrapped(token: dict):
            save_token_fn(Token(**token))

        super().__init__(
            client_id=settings.SPOTIFY_CLIENT_ID,
            scope=[s for s in Scope],
            auto_refresh_url=TOKEN_URL,
            token=serialized_token,
            token_updater=save_token_fn_wrapped,
            redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        )

    def get_auth_request(self) -> AuthRequest:
        url, state = self.authorization_url(AUTH_URL)
        return AuthRequest(url=url, state=state)

    def get_auth_token(self, auth_response: str) -> Token:
        token = self.fetch_token(
            TOKEN_URL,
            auth=HTTPBasicAuth(
                settings.SPOTIFY_CLIENT_ID,
                settings.SPOTIFY_CLIENT_SECRET,
            ),
            authorization_response=auth_response,
        )
        return Token(**token)

    def refresh(self) -> None:
        token = super().refresh_token(
            TOKEN_URL,
            auth=HTTPBasicAuth(
                settings.SPOTIFY_CLIENT_ID,
                settings.SPOTIFY_CLIENT_SECRET,
            ),
        )
        if self.token_updater:
            self.token_updater(token)

    def get_current_user(self) -> User:
        response = self.get(f"{BASE_API_URL}/me")
        return User(**response.json())

    def get_recently_played_tracks(self) -> list[RecentlyPlayedTrack]:
        response = self.get(f"{BASE_API_URL}/me/player/recently-played")
        # TODO eventually we want to control pagination
        parsed_response = PaginatedResponse[RecentlyPlayedTrack](**response.json())
        return parsed_response.items

    def _get_all[T](
        self, start_url: str, base_cls: type[T], max_count: int | None = None
    ) -> list[T]:
        items = []
        url = start_url
        while url is not None:
            raw_response = self.get(url)
            response = PaginatedResponse[base_cls](**raw_response.json())
            items.extend(response.items)
            url = response.next
            if max_count is not None and len(items) >= max_count:
                break
        if max_count is not None:
            items = items[:max_count]
        return items


class UserPlaylistResource:
    def __init__(self, session: Session):
        self.session = session
        self.user = session.get_current_user()
        self.base_url = f"{BASE_API_URL}/users/{self.user.id}/playlists"

    def create(
        self,
        name: str,
        public: bool,
        collaborative: bool,
        description: str,
    ) -> UserPlaylist:
        response = self.session.post(
            self.base_url,
            json=dict(
                name=name,
                public=public,
                collaborative=collaborative,
                description=description,
            ),
        )
        return UserPlaylist(**response.json())

    def list(self, max_count: int | None = None) -> List[UserPlaylist]:
        return self.session._get_all(self.base_url, UserPlaylist, max_count)

    def _track_url(self, id: str) -> str:
        return f"{self.base_url}/{id}/tracks"

    def list_tracks(self, id: str, max_count: int | None = None) -> List[PlaylistTrack]:
        return self.session._get_all(self._track_url(id), PlaylistTrack, max_count)

    def add_tracks(self, id: str, track_ids: List[str]) -> Any:
        assert len(track_ids) < 100  # TODO this is an API limitation, can batch later
        body = dict(uris=[Track.get_uri(tid) for tid in track_ids])
        return self.session.post(self._track_url(id), json=body)

    def remove_tracks(self, id: str, track_ids: List[str]):
        assert len(track_ids) < 100  # TODO this is an API limitation, can batch later
        return self.session.delete(
            self._track_url(id),
            json=dict(
                tracks=[dict(uri=Track.get_uri(tid)) for tid in track_ids],
            ),
        )
