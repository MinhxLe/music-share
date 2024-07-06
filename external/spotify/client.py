from collections.abc import Callable
from datetime import datetime
from enum import StrEnum

from requests.auth import HTTPBasicAuth
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
        token = super().refresh_token(TOKEN_URL)
        if self.token_updater:
            self.token_updater(token)
