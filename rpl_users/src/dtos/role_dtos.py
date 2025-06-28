from pydantic import BaseModel

from rpl_users.src.repositories.models.course_user import CourseUser
from rpl_users.src.repositories.models.role import Role

import datetime


class RoleResponseDTO(BaseModel):
    id: int
    name: str
    permissions: list[str]
    date_created: datetime.datetime
    last_updated: datetime.datetime

    @classmethod
    def from_role(cls, role: "Role") -> "RoleResponseDTO":
        return cls(
            id=role.id,
            name=role.name,
            permissions=role.get_permissions(),
            date_created=(role.date_created - datetime.timedelta(hours=3)),
            last_updated=(role.last_updated - datetime.timedelta(hours=3)),
        )

    @classmethod
    def from_course_user(cls, course_user: "CourseUser") -> "RoleResponseDTO":
        return cls.from_role(course_user.role)
