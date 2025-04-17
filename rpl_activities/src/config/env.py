from dotenv import load_dotenv
import os

load_dotenv(override=True)

DB_URL = os.getenv("DB_URL")
FRONTEND_URL = os.getenv("FRONTEND_URL")

if not all(
    [
        DB_URL,
        # FRONTEND_URL,
    ]
):
    raise ValueError("Missing environment variables")
