from rpl_users.src.dtos.user import UserCreateDTO
from .base import BaseRepository

from .models.user import User
import sqlalchemy as sa


class UsersRepository(BaseRepository):

    def create_user(self, user_data: UserCreateDTO, hashed_password: str) -> User:
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password=hashed_password,
            name=user_data.name,
            surname=user_data.surname,
            student_id=user_data.student_id,
            degree=user_data.degree,
            university=user_data.university,
            email_validated=False,
            is_admin=False,
        )
        self.db_session.add(new_user)
        self.db_session.commit()
        self.db_session.refresh(new_user)
        return new_user

    def get_user_by_username(self, username: str) -> User:
        return self.db_session.execute(
            sa.select(User).where(User.username == username)
        ).scalar_one_or_none()

    def get_user_by_email(self, email: str) -> User:
        return self.db_session.execute(
            sa.select(User).where(User.email == email)
        ).scalar_one_or_none()

    def get_user_by_id(self, user_id: str) -> User:
        return self.db_session.execute(
            sa.select(User).where(User.id == user_id)
        ).scalar_one_or_none()

    def update_user(self, user: User) -> User:
        self.db_session.commit()
        self.db_session.refresh(user)
        return user
