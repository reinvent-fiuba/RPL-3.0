from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

auth_handler = HTTPBearer()
AuthDependency = Annotated[HTTPAuthorizationCredentials, Depends(auth_handler)]
