from fastapi import APIRouter
from foo.api.router import router as foo_router

api_router = APIRouter()
api_router.include_router(foo_router, prefix="/foo")
