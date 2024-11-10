from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.metadata_params import FASTAPI_METADATA

import root.routes


app = FastAPI(**FASTAPI_METADATA)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(root.routes.router)
# app.include_router(users.routes.router)
