from fastapi import FastAPI
import httpx

from rpl_activities.src.config import env


def set_users_api_conn(app: FastAPI):
    @app.on_event("startup")
    def startup():
        app.state.users_api_client = httpx.Client(base_url=env.USERS_API_URL)
    
    app.on_event("shutdown")
    def shutdown():
        if hasattr(app.state, 'users_api_client'):
            app.state.users_api_client.close()
        app.state.users_api_client = None

