from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    declared_attr,
    mapped_column,
)

import uuid
from datetime import datetime

from sqlalchemy import (
    TIMESTAMP,
    MetaData,
    Text,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    declared_attr,
    mapped_column,
)
from core.utils import string_utils


def primary_id_column() -> Mapped[uuid.UUID]:
    return mapped_column(
        primary_key=True, init=False, server_default=func.gen_random_uuid()
    )


# These are meant as debug columns. Do not use for application level logic.
def _debug_created_at_column() -> Mapped[datetime]:
    return mapped_column(init=False, server_default=func.now())


def _debug_updated_at_column() -> Mapped[datetime]:
    return mapped_column(init=False, server_default=func.now(), onupdate=func.now())


metadata = MetaData(schema="music_share")


class Base(MappedAsDataclass, DeclarativeBase, kw_only=True):  # type: ignore
    metadata = metadata
    type_annotation_map = {
        datetime: TIMESTAMP(timezone=True),
        str: Text(),
    }

    id: Mapped[uuid.UUID] = primary_id_column()
    _debug_created_at: Mapped[datetime] = _debug_created_at_column()
    _debug_updated_at: Mapped[datetime] = _debug_updated_at_column()

    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        return string_utils.plural(string_utils.camel_to_snake(cls.__name__))
