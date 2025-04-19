from rpl_activities.src.dtos.category_dtos import CategoryCreationDTO
from rpl_activities.src.repositories.base import BaseRepository
import sqlalchemy as sa
from .models.activity_category import ActivityCategory


class CategoriesRepository(BaseRepository):
    def create_category(self, category_data: CategoryCreationDTO) -> ActivityCategory:
        new_category = ActivityCategory(
            course_id=category_data.course_id,
            name=category_data.name,
            description=category_data.description,
            date_created=category_data.date_created,
            last_updated=category_data.last_updated,
            active=category_data.active,
        )
        self.db_session.add(new_category)
        self.db_session.commit()
        self.db_session.refresh(new_category)
        return new_category
