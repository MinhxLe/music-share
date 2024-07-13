from datetime import datetime
from enum import StrEnum
from sqlalchemy import UUID, Index, UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column
from core.db.models import Base, Enum, ForeignKey


class User(Base):
    class Status(StrEnum):
        NEW = "new"
        PENDING = "pending"
        COMPLETE = "complete"

    phone_number: Mapped[str] = mapped_column(unique=True)
    status: Mapped[Status] = mapped_column(Enum(Status))


class OtpRequest(Base):
    class Status(StrEnum):
        PENDING = "pending"
        EXPIRED = "expired"

    user_id: Mapped[UUID] = mapped_column(ForeignKey(User))
    code: Mapped[str]
    status: Mapped[Status] = mapped_column(Enum(Status))
    expires_at: Mapped[datetime]

    __table_args__ = (
        Index(
            "user_id", "status", unique=True, postgresql_where=status == Status.PENDING
        ),
    )
