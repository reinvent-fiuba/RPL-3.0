import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from .config.api_metadata import FASTAPI_METADATA

from .routers.users import router as users_router
from .routers.courses import router as courses_router

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager
from pytz import utc
from rpl_users.src.schedule import cleanup_validation_tokens_job


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for the FastAPI application.
    This function is called when the application starts.
    It initializes the APScheduler and sets up a job to run weekly.
    """
    scheduler = BackgroundScheduler(timezone=utc)
    scheduler.start()

    # Trigger every Saturday at 00:00
    trigger = CronTrigger(
        day_of_week="sat",
        hour=0,
        minute=0,
        second=0,
    )
    # Add a job to the scheduler
    scheduler.add_job(
        func=cleanup_validation_tokens_job,
        trigger=trigger,
        id="weekly_data_cleanup",
        replace_existing=True,
    )
    yield

    # Gratefully shutdown the scheduler when the app is shutting down
    scheduler.shutdown()


app = FastAPI(**FASTAPI_METADATA, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users_router)
app.include_router(courses_router)

# ==============================================================================


@app.get("/", include_in_schema=False)
def root_docs_redirect():
    return RedirectResponse(url="/docs")


@app.get("/api/v3/health")
def health_ping():
    return "pong"
