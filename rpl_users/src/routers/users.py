from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

# from src.config.database import get_db_session
# import src.service as service
# from src.dtos.user import AuthUserDTO


bearer_header = HTTPBearer()
router = APIRouter(prefix="/api/v2", tags=["Users"])
