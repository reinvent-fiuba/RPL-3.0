from rpl_users.src.dtos.role import RoleResponseDTO
from .base import BaseRepository

from .models.role import Role
import sqlalchemy as sa


class RolesRepository(BaseRepository):
    def __parse_permissions(self, permissions: str) -> list[str]:
        return [permission.strip() for permission in permissions.split(",")]

    def get_all(self) -> list[RoleResponseDTO]:
        roles = self.db_session.execute(sa.select(Role)).scalars().all()
        return [
            RoleResponseDTO(
                id=role.id,
                name=role.name,
                permissions=self.__parse_permissions(role.permissions),
            )
            for role in roles
        ]
