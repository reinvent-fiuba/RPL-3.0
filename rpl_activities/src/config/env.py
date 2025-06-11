from dotenv import load_dotenv
import os

FASTAPI_PRODUCTION_PROFILE = os.getenv("FASTAPI_PRODUCTION_PROFILE")
if FASTAPI_PRODUCTION_PROFILE is None:
    load_dotenv(override=True)

DB_URL = os.getenv("DB_URL")
QUEUE_URL = os.getenv("QUEUE_URL")
USERS_API_URL = os.getenv("USERS_API_URL")
RUNNER_API_KEY = os.getenv("RUNNER_API_KEY")

if not all([DB_URL, QUEUE_URL, USERS_API_URL, RUNNER_API_KEY]):
    raise ValueError("Missing environment variables")
