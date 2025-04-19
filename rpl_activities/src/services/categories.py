from fastapi import HTTPException, status
from rpl_activities.src.deps.auth import CurrentCourseUser
from rpl_activities.src.dtos.category_dtos import CategoryCreationDTO
from rpl_activities.src.repositories.categories import CategoriesRepository
from rpl_activities.src.repositories.models.activity_category import ActivityCategory


class CategoriesService:
    def __init__(self, db):
        self.categories_repo = CategoriesRepository(db)

    def create_category(
        self,
        current_course_user: CurrentCourseUser,
        course_id: int,
        category_data: CategoryCreationDTO,
    ) -> CategoryCreationDTO:
        if not current_course_user.has_authority("activity_manage"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to create a category",
            )
        created_category: ActivityCategory = self.categories_repo.create_category(
            course_id, category_data
        )
        return CategoryCreationDTO(
            course_id=created_category.course_id,
            name=created_category.name,
            description=created_category.description,
            date_created=created_category.date_created,
            last_updated=created_category.last_updated,
            active=created_category.active,
        )
