from typing import List, Optional
from fastapi import APIRouter, status
from rpl_users.src.deps.auth import CurrentUserDependency
from rpl_users.src.deps.email import EmailHandlerDependency
from rpl_users.src.dtos.user_dtos import (
    FindUsersResponseDTO,
    ResendEmailValidationDTO,
    UserCreationDTO,
    UserForgotPasswordDTO,
    UserLoginDTO,
    UserLoginResponseDTO,
    UserPasswordResetDTO,
    UserProfileResponseDTO,
    UserProfileUpdateDTO,
    UserEmailValidationDTO,
)
from rpl_users.src.deps.database import DBSessionDependency
from rpl_users.src.services.users import UsersService


router = APIRouter(prefix="/api/v3", tags=["Users"])


# ==============================================================================


@router.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreationDTO, email_handler: EmailHandlerDependency, db: DBSessionDependency):
    return UsersService(db).create_user(user_data, email_handler)


@router.post("/auth/resendValidationEmail")
def resend_validation_email(
    user_data: ResendEmailValidationDTO, email_handler: EmailHandlerDependency, db: DBSessionDependency
):
    return UsersService(db).resend_validation_email(user_data, email_handler)


@router.post("/auth/validateEmail")
def validate_email(
    validation_data: UserEmailValidationDTO, email_handler: EmailHandlerDependency, db: DBSessionDependency
):
    return UsersService(db).validate_email(validation_data, email_handler)


@router.post("/auth/forgotPassword", response_model=UserForgotPasswordDTO)
def forgot_password(
    user_data: UserForgotPasswordDTO, email_handler: EmailHandlerDependency, db: DBSessionDependency
):
    return UsersService(db).forgot_password(user_data, email_handler)


@router.post("/auth/resetPassword", response_model=UserProfileResponseDTO)
def reset_password(user_data: UserPasswordResetDTO, db: DBSessionDependency):
    return UsersService(db).reset_password(user_data)


@router.post("/auth/login", response_model=UserLoginResponseDTO)
def login_user(user_data: UserLoginDTO, db: DBSessionDependency):
    return UsersService(db).login_user(user_data)


# ==============================================================================


@router.get("/auth/profile", response_model=UserProfileResponseDTO)
def get_user_profile(current_user: CurrentUserDependency, db: DBSessionDependency):
    return UsersService(db).get_user_profile(current_user)


@router.patch("/auth/profile", response_model=UserProfileResponseDTO)
def update_user_profile(
    new_profile_info: UserProfileUpdateDTO, current_user: CurrentUserDependency, db: DBSessionDependency
):
    return UsersService(db).update_user_profile(current_user, new_profile_info)


@router.get("/users", response_model=List[FindUsersResponseDTO])
def find_users(current_user: CurrentUserDependency, db: DBSessionDependency, query: Optional[str] = ""):
    return UsersService(db).find_users(query, current_user)


# ==============================================================================
