from dotenv import load_dotenv
import os

FASTAPI_PRODUCTION_PROFILE = os.getenv("FASTAPI_PRODUCTION_PROFILE")
if FASTAPI_PRODUCTION_PROFILE is None:
    load_dotenv(override=True)

FRONTEND_URL = os.getenv("FRONTEND_URL")
DB_URL = os.getenv("DB_URL")

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXPIRE_MINUTES = os.getenv("JWT_EXPIRE_MINUTES")

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
RPL_HELP_EMAIL_USER = os.getenv("RPL_HELP_EMAIL_USER")
RPL_HELP_EMAIL_PASSWORD = os.getenv("RPL_HELP_EMAIL_PASSWORD")

ACTIVITIES_API_URL = os.getenv("ACTIVITIES_API_URL")

if not all(
    [
        FRONTEND_URL,
        DB_URL,
        JWT_SECRET,
        JWT_ALGORITHM,
        JWT_EXPIRE_MINUTES,
        SMTP_SERVER,
        SMTP_PORT,
        RPL_HELP_EMAIL_USER,
        RPL_HELP_EMAIL_PASSWORD,
        ACTIVITIES_API_URL,
    ]
):
    raise ValueError("Missing environment variables")
