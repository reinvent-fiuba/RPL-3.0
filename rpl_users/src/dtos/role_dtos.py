from pydantic import BaseModel

from rpl_users.src.repositories.models.course_user import CourseUser

import datetime


class RoleResponseDTO(BaseModel):
    id: int
    name: str
    permissions: list[str]
    date_created: datetime.datetime
    last_updated: datetime.datetime

    @classmethod
    def from_course_user(cls, course_user: "CourseUser") -> "RoleResponseDTO":
        return cls(
            id=course_user.role.id,
            name=course_user.role.name,
            permissions=course_user.role.permissions.split(","),
            date_created=course_user.role.date_created,
            last_updated=course_user.role.last_updated,
        )
