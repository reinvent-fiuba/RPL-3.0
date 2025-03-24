from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from .config.api_metadata import FASTAPI_METADATA

# from .routers.courses import router as courses_router

app = FastAPI(**FASTAPI_METADATA)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(courses_router)


@app.get("/", include_in_schema=False)
def root_docs_redirect():
    return RedirectResponse(url="/docs")


@app.get("/api/v2/health")
def health_ping():
    return "pong"
