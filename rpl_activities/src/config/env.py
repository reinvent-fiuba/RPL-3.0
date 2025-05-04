from dotenv import load_dotenv
import os

FASTAPI_PRODUCTION_PROFILE = os.getenv("FASTAPI_PRODUCTION_PROFILE")
if FASTAPI_PRODUCTION_PROFILE is None:
    load_dotenv(override=True)

DB_URL = os.getenv("DB_URL")
FRONTEND_URL = os.getenv("FRONTEND_URL")
USERS_API_URL = os.getenv("USERS_API_URL")

if not all(
    [
        DB_URL,
        # FRONTEND_URL,
        USERS_API_URL,
    ]
):
    raise ValueError("Missing environment variables")
