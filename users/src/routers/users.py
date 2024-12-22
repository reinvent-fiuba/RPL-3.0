from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

# from utils.setup import get_db_session
# import users.service as service
# from users.dtos.models import AuthUserDTO


bearer_header = HTTPBearer()
router = APIRouter(prefix="/api/v2", tags=["Users"])
