from contextlib import asynccontextmanager
from fastapi import FastAPI
import httpx
from rpl_activities.src.config import env


@asynccontextmanager
async def users_api_conn_lifespan(app: FastAPI):
    async with httpx.AsyncClient(
        base_url=env.USERS_API_URL,
        timeout=httpx.Timeout(60.0),
    ) as client:
        yield {"users_api_client": client}
