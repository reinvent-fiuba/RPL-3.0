from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from rpl_users.src.dtos.user import (
    UserCreateDTO,
    UserLoginDTO,
    UserLoginResponseDTO,
    UserProfileResponseDTO,
    UserProfileUpdateDTO,
)
from rpl_users.src.config.database import get_db_session
from rpl_users.src.services.users import UsersService


bearer_header = HTTPBearer()
router = APIRouter(prefix="/api/v2", tags=["Users"])


@router.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreateDTO, db: Session = Depends(get_db_session)):
    return UsersService(db).create_user(user_data)


@router.post("/auth/login", response_model=UserLoginResponseDTO)
def login_user(user_data: UserLoginDTO, db: Session = Depends(get_db_session)):
    return UsersService(db).login_user(user_data)


@router.get("/auth/profile", response_model=UserProfileResponseDTO)
def get_user_profile(
    auth_header: HTTPAuthorizationCredentials = Depends(bearer_header),
    db: Session = Depends(get_db_session),
):
    return UsersService(db).get_user_profile(auth_header.credentials)


@router.put("/auth/profile", response_model=UserProfileResponseDTO)
def update_user_profile(
    profile_data: UserProfileUpdateDTO,
    auth_header: HTTPAuthorizationCredentials = Depends(bearer_header),
    db: Session = Depends(get_db_session),
):
    return UsersService(db).update_user_profile(auth_header.credentials, profile_data)
