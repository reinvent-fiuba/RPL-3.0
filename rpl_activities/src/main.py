from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from rpl_activities.src.config.api_lifespan import users_api_conn_lifespan
from .config.api_metadata import FASTAPI_METADATA

from .routers.categories import router as categories_router
from .routers.rpl_files import router as rpl_files_router

# from .routers.activities import router as activities_router


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


# ==============================================================================


@app.get("/", include_in_schema=False)
def root_docs_redirect():
    return RedirectResponse(url="/docs")


@app.get("/api/v3/health")
def health_ping():
    return "pong"
