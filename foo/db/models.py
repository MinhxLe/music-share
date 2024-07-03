from sqlalchemy.orm import Mapped
from core.db.models import Base


class Foo(Base):
    name: Mapped[str]
