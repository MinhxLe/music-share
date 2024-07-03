from fastapi import FastAPI
from main.router import api_router

app = FastAPI()

app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    # Add startup code here
    pass


@app.on_event("shutdown")
async def shutdown_event():
    # Add shutdown code here
    pass
