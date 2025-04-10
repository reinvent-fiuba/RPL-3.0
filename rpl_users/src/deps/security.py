import re
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from rpl_users.src.config.env import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES


hasher = PasswordHash((BcryptHasher(rounds=10),))


def hash_password(password: str) -> str:
    hash = hasher.hash(password)
    return hash


def verify_password(plain_password: str, hashed_password: str) -> bool:
    valid = hasher.verify(plain_password, hashed_password)
    return valid


# =============================================================================


def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=int(JWT_EXPIRE_MINUTES)),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def verify_access_token(token: str) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired JWT token",
        )
    except jwt.PyJWKError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid JWT token",
        )


def is_login_via_email(username_or_email: str) -> bool:
    email_regex = r"^[a-zA-Z0-9_!#$%&’*+/=?`{|}~^.-]+@[a-zA-Z0-9.-]+$"
    if not re.match(email_regex, username_or_email):
        return False
    return True
