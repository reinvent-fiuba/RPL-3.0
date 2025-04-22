from typing import Optional
from pydantic import BaseModel, EmailStr


class ExternalCurrentMainUserDTO(BaseModel):
    id: int
    username: str
    email: EmailStr
    name: str
    surname: str
    student_id: str
    degree: str
    university: str
    is_admin: bool
    img_uri: Optional[str] = None
