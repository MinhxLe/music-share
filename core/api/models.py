import uuid
from pydantic import BaseModel as BaseModel

class Resource(BaseModel):
    id: uuid.UUID
