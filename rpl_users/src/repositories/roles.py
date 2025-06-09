from typing import Optional
from .base import BaseRepository

from .models.role import Role

import sqlalchemy as sa


class RolesRepository(BaseRepository):

    # ====================== QUERYING ====================== #

    def get_all_roles(self) -> list[Role]:
        return self.db_session.execute(sa.select(Role)).scalars().all()

    def get_role_named(self, name: str) -> Optional[Role]:
        return self.db_session.execute(sa.select(Role).where(Role.name == name)).scalar_one_or_none()
