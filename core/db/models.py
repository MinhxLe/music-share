import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    TIMESTAMP,
    MetaData,
    Text,
    func,
)
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey as SqlForeignKey
from sqlalchemy.dialects.postgresql import JSONB
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
def created_at_column() -> Mapped[datetime]:
    return mapped_column(init=False, server_default=func.now())


def updated_at_column() -> Mapped[datetime]:
    return mapped_column(init=False, server_default=func.now(), onupdate=func.now())


metadata = MetaData()


class Base(MappedAsDataclass, DeclarativeBase, kw_only=True):  # type: ignore
    metadata = metadata
    type_annotation_map = {
        datetime: TIMESTAMP(timezone=True),
        str: Text(),
        dict: JSONB,
    }

    id: Mapped[uuid.UUID] = primary_id_column()
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()

    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        return string_utils.plural(string_utils.camel_to_snake(cls.__name__))


# Wrapping types here so we have some controls and standardization
class ForeignKey(SqlForeignKey):
    def __init__(
        self,
        to: type[Base],
        legacy_pk_field_name: Optional[str] = None,
    ) -> None:
        pk_field_name = legacy_pk_field_name or "id"
        super().__init__(
            f"{to.__tablename__}.{pk_field_name}",
            onupdate="CASCADE",
            ondelete="CASCADE",
        )


class Enum(SqlEnum):
    def __init__(self, *args: Any, **kwargs: Any):
        # kwargs["validate_strings"] = False
        kwargs["native_enum"] = False
        kwargs["values_callable"] = lambda x: [i.value for i in x]
        super().__init__(*args, **kwargs)
