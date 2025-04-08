from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from rpl_users.src.deps import security
from rpl_users.src.deps.database import DBSessionDependency
from rpl_users.src.repositories.models.user import User
from rpl_users.src.repositories.users import UsersRepository

# Dependencies =============================

auth_handler = HTTPBearer()
AuthDependency = Annotated[HTTPAuthorizationCredentials, Depends(auth_handler)]

# ==========================================


def get_current_user(
    auth_header: AuthDependency, db_session: DBSessionDependency
) -> User:
    user_id = security.verify_access_token(auth_header.credentials)
    users_repo = UsersRepository(db_session)
    user = users_repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


CurrentUserDependency = Annotated[
    User,
    Depends(get_current_user),
]

# ==========================================
