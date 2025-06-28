from datetime import datetime, timezone
from typing import Optional
from rpl_users.src.dtos.user_dtos import UserCreationDTO
from .base import BaseRepository

from .models.user import User
import sqlalchemy as sa


class UsersRepository(BaseRepository):

    # ====================== MANAGING ====================== #

    def save_new_user(self, user_data: UserCreationDTO, hashed_password: str) -> User:
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

    def update_user(self, user: User) -> User:
        user.last_updated = datetime.now(timezone.utc)
        self.db_session.commit()
        self.db_session.refresh(user)
        return user

    # ====================== PRIVATE - QUERYING ====================== #

    def __select_matching_username_or_fullname(self, username_or_fullname: str) -> sa.sql.expression.Select:
        split_fullname = username_or_fullname.split()
        if len(split_fullname) == 1:
            return sa.select(User).where(
                sa.or_(
                    User.username.ilike(f"%{username_or_fullname}%"),
                    User.name.ilike(f"%{username_or_fullname}%"),
                    User.surname.ilike(f"%{username_or_fullname}%"),
                )
            )
        else:
            fullname_direct_matching = "%".join(split_fullname)
            first_part = split_fullname[0]
            last_part = split_fullname[-1]
            return sa.select(User).where(
                sa.or_(
                    User.username.ilike(f"%{username_or_fullname}%"),
                    User.name.ilike(f"%{username_or_fullname}%"),
                    User.surname.ilike(f"%{username_or_fullname}%"),
                    sa.func.concat(User.name, " ", User.surname).ilike(f"%{fullname_direct_matching}%"),
                    User.name.ilike(f"%{first_part}%"),
                    User.surname.ilike(f"%{last_part}%"),
                    User.name.ilike(f"%{last_part}%"),
                    User.surname.ilike(f"%{first_part}%"),
                )
            )

    # ====================== QUERYING ====================== #

    def get_user_with_username(self, username: str) -> Optional[User]:
        return self.db_session.execute(sa.select(User).where(User.username == username)).scalar_one_or_none()

    def get_user_with_email(self, email: str) -> Optional[User]:
        return self.db_session.execute(sa.select(User).where(User.email == email)).scalar_one_or_none()

    def get_user_with_id(self, user_id: int) -> Optional[User]:
        return self.db_session.execute(sa.select(User).where(User.id == user_id)).scalar_one_or_none()

    def get_all_users_with_username_or_fullname(self, username_or_fullname: str) -> list[User]:
        if not username_or_fullname:
            return self.db_session.execute(sa.select(User).limit(30).order_by(User.id)).scalars().all()
        else:
            return (
                self.db_session.execute(
                    self.__select_matching_username_or_fullname(username_or_fullname)
                    .limit(30)
                    .order_by(User.id)
                )
                .scalars()
                .all()
            )
