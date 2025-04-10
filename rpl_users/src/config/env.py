from dotenv import load_dotenv
import os

load_dotenv()

DB_URL = os.getenv("DB_URL")
FRONTEND_URL = os.getenv("FRONTEND_URL")

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXPIRE_MINUTES = os.getenv("JWT_EXPIRE_MINUTES")

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

if not all(
    [
        DB_URL,
        # FRONTEND_URL,
        JWT_SECRET,
        JWT_ALGORITHM,
        JWT_EXPIRE_MINUTES,
        # SMTP_SERVER,
        # SMTP_PORT,
        # SMTP_USER,
        # SMTP_PASSWORD,
    ]
):
    raise ValueError("Missing environment variables")
