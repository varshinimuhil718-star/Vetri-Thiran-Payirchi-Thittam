from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .database import init_db
from .routes.api import router as api_router
from .routes.web import router as web_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="FitBuddy API",
    description="AI-powered 7-day fitness plan generator.",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(web_router)
app.include_router(api_router)
