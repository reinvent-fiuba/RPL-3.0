from datetime import datetime, timezone
import logging
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from rpl_users.src.deps.email import EmailHandler
from rpl_users.src.dtos.role_dtos import RoleResponseDTO
from rpl_users.src.dtos.university_dtos import UniversityResponseDTO
from rpl_users.src.repositories.models.user import User
from rpl_users.src.dtos.user_dtos import (
    CurrentMainUserResponseDTO,
    FindUsersResponseDTO,
    ResendEmailValidationDTO,
    UserCreationDTO,
    UserEmailValidationDTO,
    UserForgotPasswordDTO,
    UserLoginDTO,
    UserLoginResponseDTO,
    UserPasswordResetDTO,
    UserProfileResponseDTO,
    UserCreationResponseDTO,
    UserProfileUpdateDTO,
)
from rpl_users.src.repositories.roles import RolesRepository
from rpl_users.src.repositories.universities import UniversitiesRepository
from rpl_users.src.repositories.users import UsersRepository
from rpl_users.src.repositories.validation_tokens import ValidationTokensRepository
import rpl_users.src.deps.security as security


class UsersService:
    def __init__(self, db_session: Session):
        self.users_repo = UsersRepository(db_session)
        self.validation_tokens_repo = ValidationTokensRepository(db_session)

    def __verify_username_and_email_availability(self, username: str, email: str):
        existing_user = self.users_repo.get_user_with_username(username)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
        existing_user = self.users_repo.get_user_with_email(email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    def __get_user_by_username_or_email(self, username_or_email: str) -> User:
        if security.is_login_via_email(username_or_email):
            user = self.users_repo.get_user_with_email(username_or_email)
        else:
            user = self.users_repo.get_user_with_username(username_or_email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    def __verify_user_login(self, user_data: UserLoginDTO) -> User:
        user = self.__get_user_by_username_or_email(user_data.username_or_email)
        if not user.email_validated:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not validated")

        valid = security.verify_password(user_data.password, user.password)
        if not valid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        logging.getLogger("uvicorn.error").info(
            f"[users:services] User {user.username} logged in successfully"
        )
        return user

    def __send_validation_email(self, user_id, email: str, email_handler: EmailHandler):
        token = email_handler.send_validation_email(email)
        self.validation_tokens_repo.save_new_validation_token(user_id, token)

    def __verify_token(self, token: str):
        token_data = self.validation_tokens_repo.get_by_token(token)
        if not token_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

        expiration_date = token_data.expiration_date
        # this always comes in UTC, but we replace to ensure the comparison
        if expiration_date.tzinfo is None:
            expiration_date = expiration_date.replace(tzinfo=timezone.utc)
        if expiration_date < datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired")
        return token_data

    # =============================================================================

    def create_user(self, user_data: UserCreationDTO, email_handler: EmailHandler) -> UserCreationResponseDTO:
        self.__verify_username_and_email_availability(user_data.username, user_data.email)
        hashed_password = security.hash_password(user_data.password)
        new_user = self.users_repo.save_new_user(user_data, hashed_password)
        self.__send_validation_email(new_user.id, user_data.email, email_handler)
        return UserCreationResponseDTO(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            name=new_user.name,
            surname=new_user.surname,
            student_id=new_user.student_id,
            degree=new_user.degree,
            university=new_user.university,
        )

    def resend_validation_email(self, user_data: ResendEmailValidationDTO, email_handler: EmailHandler):
        user = self.__get_user_by_username_or_email(user_data.username_or_email)
        if user.email_validated:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already validated")
        self.__send_validation_email(user.id, user.email, email_handler)

    def validate_email(self, validation_data: UserEmailValidationDTO):
        token_data = self.__verify_token(validation_data.token)
        user = token_data.user
        if user.email_validated:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already validated")
        user.email_validated = True
        user = self.users_repo.update_user(user)
        self.validation_tokens_repo.delete_by_token(validation_data.token)
        logging.getLogger("uvicorn.error").info(
            f"[users:services] User {user.username} validated email successfully"
        )

    def login_user(self, user_data: UserLoginDTO) -> UserLoginResponseDTO:
        user = self.__verify_user_login(user_data)
        access_token = security.create_access_token(user.id)
        return UserLoginResponseDTO(access_token=access_token, token_type="Bearer")

    def forgot_password(
        self, user_data: UserForgotPasswordDTO, email_handler: EmailHandler
    ) -> UserForgotPasswordDTO:
        user = self.__get_user_by_username_or_email(user_data.email)
        token = email_handler.send_password_reset_email(user.email)
        self.validation_tokens_repo.save_new_validation_token(user.id, token)
        logging.getLogger("uvicorn.error").info(
            f"[users:services] Password reset email sent to {user.username}"
        )
        return user_data

    def reset_password(self, user_data: UserPasswordResetDTO) -> UserProfileResponseDTO:
        token_data = self.__verify_token(user_data.token)
        user = token_data.user
        hashed_new_password = security.hash_password(user_data.new_password)
        user.password = hashed_new_password
        user = self.users_repo.update_user(user)
        self.validation_tokens_repo.delete_by_token(user_data.token)
        logging.getLogger("uvicorn.error").info(
            f"[users:services] Password reset successful for {user.username}"
        )
        return UserProfileResponseDTO(
            username=user.username,
            name=user.name,
            surname=user.surname,
            email=user.email,
            is_admin=user.is_admin,
            student_id=user.student_id,
            degree=user.degree,
            university=user.university,
            img_uri=user.img_uri,
        )

    # =============================================================================

    def get_user_profile(self, user: User) -> UserProfileResponseDTO:
        return UserProfileResponseDTO(
            username=user.username,
            name=user.name,
            surname=user.surname,
            email=user.email,
            is_admin=user.is_admin,
            student_id=user.student_id,
            degree=user.degree,
            university=user.university,
            img_uri=user.img_uri,
        )

    def update_user_profile(
        self, user: User, new_profile_info: UserProfileUpdateDTO
    ) -> UserProfileResponseDTO:
        for key, value in new_profile_info.model_dump().items():
            if value is not None:
                setattr(user, key, value)

        user = self.users_repo.update_user(user)
        return UserProfileResponseDTO(
            username=user.username,
            name=user.name,
            surname=user.surname,
            email=user.email,
            is_admin=user.is_admin,
            student_id=user.student_id,
            degree=user.degree,
            university=user.university,
            img_uri=user.img_uri,
        )

    def find_users(self, username_or_fullname: str, current_user: User) -> List[FindUsersResponseDTO]:
        if not current_user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
        users = self.users_repo.get_all_users_with_username_or_fullname(username_or_fullname)
        return [
            FindUsersResponseDTO(
                id=user.id,
                username=user.username,
                email=user.email,
                name=user.name,
                surname=user.surname,
                student_id=user.student_id,
                degree=user.degree,
                university=user.university,
            )
            for user in users
        ]

    # =============================================================================

    def get_user_for_ext_service(self, current_user: User) -> CurrentMainUserResponseDTO:
        return CurrentMainUserResponseDTO(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            name=current_user.name,
            surname=current_user.surname,
            student_id=current_user.student_id,
            degree=current_user.degree,
            university=current_user.university,
            is_admin=current_user.is_admin,
        )
