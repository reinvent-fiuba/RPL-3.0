from rpl_users.src.dtos.university_dtos import UniversityResponseDTO
from .base import BaseRepository

from .models.university import University
import sqlalchemy as sa


class UniversitiesRepository(BaseRepository):
    def __parse_degrees(self, degrees: str) -> list[str]:
        return [degree.strip() for degree in degrees.split(",")]

    def get_all(self) -> list[UniversityResponseDTO]:
        universities = self.db_session.execute(sa.select(University)).scalars().all()
        return [
            UniversityResponseDTO(
                id=university.id,
                name=university.name,
                degrees=self.__parse_degrees(university.degrees),
            )
            for university in universities
        ]
