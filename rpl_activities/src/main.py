from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from rpl_activities.src.config.api_metadata import FASTAPI_METADATA
from rpl_activities.src.config.api_lifespan import users_api_conn_lifespan
from rpl_activities.src.routers.categories import router as categories_router
from rpl_activities.src.routers.rpl_files import router as rplfiles_router
from rpl_activities.src.routers.activities import router as activities_router
from rpl_activities.src.routers.activity_tests import router as activity_tests_router


app = FastAPI(lifespan=users_api_conn_lifespan, **FASTAPI_METADATA)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categories_router)
app.include_router(rplfiles_router)
app.include_router(activities_router)
app.include_router(activity_tests_router)


# ==============================================================================


@app.get("/", include_in_schema=False)
def root_docs_redirect():
    return RedirectResponse(url="/docs")


@app.get("/api/v3/health")
def health_ping():
    return "pong"
