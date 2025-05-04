from dotenv import load_dotenv
import os

FASTAPI_PRODUCTION_PROFILE = os.getenv("FASTAPI_PRODUCTION_PROFILE")
if FASTAPI_PRODUCTION_PROFILE is None:
    load_dotenv(override=True)

DB_URL = os.getenv("DB_URL")
FRONTEND_URL = os.getenv("FRONTEND_URL")

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXPIRE_MINUTES = os.getenv("JWT_EXPIRE_MINUTES")

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
RPL_HELP_EMAIL_USER = os.getenv("RPL_HELP_EMAIL_USER")
RPL_HELP_EMAIL_PASSWORD = os.getenv("RPL_HELP_EMAIL_PASSWORD")

if not all(
    [
        DB_URL,
        # FRONTEND_URL,
        JWT_SECRET,
        JWT_ALGORITHM,
        JWT_EXPIRE_MINUTES,
        # SMTP_SERVER,
        # SMTP_PORT,
        # RPL_HELP_EMAIL_USER,
        # RPL_HELP_EMAIL_PASSWORD,
    ]
):
    raise ValueError("Missing environment variables")
