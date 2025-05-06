from contextlib import contextmanager
from fastapi import FastAPI
import httpx

from rpl_activities.src.config import env


@contextmanager
def users_api_conn_lifespan(app: FastAPI):
    with httpx.Client(base_url=env.USERS_API_URL) as client:
        yield {"users_api_client": client}
