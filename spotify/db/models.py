from datetime import datetime
from enum import StrEnum
import uuid

from sqlalchemy.orm import Mapped, mapped_column
from core.db.models import Base, Enum, ForeignKey
from users.db.models import User


class SpotifyAccount(Base):
    class Status(StrEnum):
        NEW = "new"
        COMPLETE = "complete"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(User), unique=True)
    status: Mapped[Status] = mapped_column(Enum(Status))


class OAuthToken(Base):
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(SpotifyAccount))
    access_token: Mapped[str]
    refresh_token: Mapped[str]
    expires_at: Mapped[datetime]
    scope: Mapped[list[str]]
    active: Mapped[bool]
