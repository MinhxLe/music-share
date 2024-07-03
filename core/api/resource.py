import uuid
from pydantic import BaseModel


class Resource(BaseModel):
    id: uuid.UUID
    class Config:
        orm_mode = True

