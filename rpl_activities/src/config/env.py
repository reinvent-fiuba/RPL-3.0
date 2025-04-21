from dotenv import load_dotenv
import os

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
