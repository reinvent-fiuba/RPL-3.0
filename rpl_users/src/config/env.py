from dotenv import load_dotenv
import os

load_dotenv()

DB_URL = os.getenv("DB_URL")
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXPIRE_MINUTES = os.getenv("JWT_EXPIRE_MINUTES")

if not DB_URL or not JWT_SECRET or not JWT_ALGORITHM or not JWT_EXPIRE_MINUTES:
    raise ValueError("Missing environment variables")
