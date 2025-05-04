from contextlib import contextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import httpx


from rpl_activities.src.config import env
from rpl_activities.src.config.api_metadata import FASTAPI_METADATA

from rpl_activities.src.routers.categories import router as categories_router
from rpl_activities.src.routers.rpl_files import router as rpl_files_router

# from rpl_activities.src.routers.activities import router as activities_router


@contextmanager
def users_api_conn_lifespan(app: FastAPI):
    with httpx.Client(base_url=env.USERS_API_URL) as client:
        yield {"users_api_client": client}


app = FastAPI(lifespan=users_api_conn_lifespan, **FASTAPI_METADATA)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categories_router)
app.include_router(rpl_files_router)
# app.include_router(activities_router)


@app.get("/", include_in_schema=False)
def root_docs_redirect():
    return RedirectResponse(url="/docs")


@app.get("/api/v3/health")
def health_ping():
    return "pong"
