from fastapi import APIRouter, status
from rpl_users.src.deps.auth import CurrentUserDependency
from rpl_users.src.dtos.user import (
    UserCreateDTO,
    UserLoginDTO,
    UserLoginResponseDTO,
    UserProfileResponseDTO,
    UserProfileUpdateDTO,
)
from rpl_users.src.deps.database import DBSessionDependency
from rpl_users.src.services.users import UsersService


router = APIRouter(prefix="/api/v3", tags=["Users"])


@router.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreateDTO, db: DBSessionDependency):
    return UsersService(db).create_user(user_data)


@router.post("/auth/login", response_model=UserLoginResponseDTO)
def login_user(user_data: UserLoginDTO, db: DBSessionDependency):
    return UsersService(db).login_user(user_data)


@router.get("/auth/profile", response_model=UserProfileResponseDTO)
def get_user_profile(current_user: CurrentUserDependency, db: DBSessionDependency):
    return UsersService(db).get_user_profile(current_user)


@router.patch("/auth/profile", response_model=UserProfileResponseDTO)
def update_user_profile(
    new_profile_info: UserProfileUpdateDTO,
    current_user: CurrentUserDependency,
    db: DBSessionDependency,
):
    return UsersService(db).update_user_profile(current_user, new_profile_info)


# ==============================================================================
