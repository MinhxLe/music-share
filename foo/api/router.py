from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.api.models import Resource
from core.db.database import get_session
from foo.db import models

router = APIRouter()

class FooResource(Resource):
    name: str

@router.get("/foos/", response_model=List[FooResource])
def foos(*, db: Session=Depends(get_session)):
    return db.query(models.Foo).all()

@router.get("/ping/")
def hi():
    return dict(hello="world")

