from rpl_users.src.dtos.university_dtos import UniversityResponseDTO
from .base import BaseRepository
from .models.university import University


import sqlalchemy as sa


class UniversitiesRepository(BaseRepository):

    # ====================== QUERYING ====================== #

    def get_all_universities(self) -> list[University]:
        return self.db_session.execute(sa.select(University)).scalars().all()
