from datetime import datetime, timezone
from rpl_activities.src.dtos.category_dtos import (
    CategoryResponseDTO,
    CategoryUpdateRequestDTO,
)
from rpl_activities.src.repositories.base import BaseRepository
import sqlalchemy as sa
from .models.activity_category import ActivityCategory


class CategoriesRepository(BaseRepository):

    def get_all_categories(self, course_id: int):
        return (
            self.db_session.execute(
                sa.select(ActivityCategory).where(
                    ActivityCategory.course_id == course_id
                )
            )
            .scalars()
            .all()
        )

    def get_active_categories(self, course_id: int):
        return (
            self.db_session.execute(
                sa.select(ActivityCategory).where(
                    ActivityCategory.course_id == course_id,
                    ActivityCategory.active == True,
                )
            )
            .scalars()
            .all()
        )

    def create_category(
        self, course_id: int, category_data: CategoryResponseDTO
    ) -> ActivityCategory:
        new_category = ActivityCategory(
            course_id=course_id,
            name=category_data.name,
            description=category_data.description,
            date_created=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc),
            active=True,
        )
        self.db_session.add(new_category)
        self.db_session.commit()
        self.db_session.refresh(new_category)
        return new_category

    def clone_category(
        self, category: ActivityCategory, to_course_id: int
    ) -> ActivityCategory:
        new_category = ActivityCategory(
            course_id=to_course_id,
            name=category.name,
            description=category.description,
            date_created=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc),
            active=category.active,
        )
        self.db_session.add(new_category)
        self.db_session.commit()
        self.db_session.refresh(new_category)
        return new_category

    def get_category_by_id_and_course_id(
        self, category_id: int, course_id: int
    ) -> ActivityCategory:
        category = (
            self.db_session.execute(
                sa.select(ActivityCategory).where(
                    ActivityCategory.id == category_id,
                    ActivityCategory.course_id == course_id,
                )
            )
            .scalars()
            .one_or_none()
        )
        return category

    def update_category(
        self,
        new_category_data: CategoryUpdateRequestDTO,
        category: ActivityCategory,
    ) -> ActivityCategory:
        if new_category_data.name is not None:
            category.name = new_category_data.name
        if new_category_data.description is not None:
            category.description = new_category_data.description
        if new_category_data.active is not None:
            category.active = new_category_data.active
        category.last_updated = datetime.now(timezone.utc)
        self.db_session.commit()
        self.db_session.refresh(category)
        return category
