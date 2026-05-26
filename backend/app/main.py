from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import admin, auth, forecasts, oil, profile
from app.scheduler.setup import shutdown_scheduler, start_scheduler
from app.utils.logging_setup.setup import setup_logging, shutdown_logging
from app.utils.rate_limit.setup import install_rate_limit

setup_logging()


@asynccontextmanager
async def lifespan(_: FastAPI):
    start_scheduler()
    yield
    shutdown_scheduler()
    shutdown_logging()


app = FastAPI(title="Python API", lifespan=lifespan)

install_rate_limit(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api"

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(profile.router, prefix=API_PREFIX)
app.include_router(admin.router, prefix=API_PREFIX)
app.include_router(oil.router, prefix=API_PREFIX)
app.include_router(forecasts.router, prefix=API_PREFIX)


@app.get("/health", tags=["health"])
async def healthcheck() -> dict:
    return {"status": "ok"}
