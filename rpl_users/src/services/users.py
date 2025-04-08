import logging
from fastapi import HTTPException, status
from rpl_users.src.repositories.models.user import User
from rpl_users.src.dtos.user import (
    UserCreateDTO,
    UserLoginDTO,
    UserLoginResponseDTO,
    UserProfileResponseDTO,
    UserCreateResponseDTO,
    UserProfileUpdateDTO,
)
from rpl_users.src.repositories.users import UsersRepository
import rpl_users.src.deps.security as security


class UsersService:
    def __init__(self, db_session):
        self.users_repo = UsersRepository(db_session)

    def __validate_username_email_availability(self, username: str, email: str):
        existing_user = self.users_repo.get_user_by_username(username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )
        existing_user = self.users_repo.get_user_by_email(email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )

    def __validate_user_login(self, user_data: UserLoginDTO) -> User:
        if security.is_login_via_email(user_data.username_or_email):
            user = self.users_repo.get_user_by_email(user_data.username_or_email)
        else:
            user = self.users_repo.get_user_by_username(user_data.username_or_email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        if not user.email_validated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email not validated",
            )

        valid = security.verify_password(user_data.password, user.password)
        if not valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        logging.info(f"[users:services] User {user.username} logged in successfully")
        return user

    # =============================================================================

    def create_user(self, user_data: UserCreateDTO) -> UserCreateResponseDTO:
        self.__validate_username_email_availability(user_data.username, user_data.email)

        hashed_password = security.hash_password(user_data.password)

        new_user = self.users_repo.create_user(
            user_data,
            hashed_password,
        )

        # TODO Send email for validation

        return UserCreateResponseDTO(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            name=new_user.name,
            surname=new_user.surname,
            student_id=new_user.student_id,
            degree=new_user.degree,
            university=new_user.university,
        )

    def login_user(self, user_data: UserLoginDTO) -> UserLoginResponseDTO:
        user = self.__validate_user_login(user_data)
        access_token = security.create_access_token(user.id)
        return UserLoginResponseDTO(
            access_token=access_token,
            token_type="Bearer",
        )

    def get_user_profile(self, user: User) -> UserProfileResponseDTO:
        return UserProfileResponseDTO(
            username=user.username,
            name=user.name,
            surname=user.surname,
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

        self.users_repo.update_user(user)
        return UserProfileResponseDTO(
            username=user.username,
            name=user.name,
            surname=user.surname,
            student_id=user.student_id,
            degree=user.degree,
            university=user.university,
            img_uri=user.img_uri,
        )
