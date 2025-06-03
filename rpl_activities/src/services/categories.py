from fastapi import HTTPException, status
from rpl_activities.src.deps.auth import CurrentCourseUser
from rpl_activities.src.dtos.category_dtos import CategoryResponseDTO
from rpl_activities.src.repositories.categories import CategoriesRepository
from rpl_activities.src.repositories.models.activity_category import ActivityCategory
from rpl_activities.src.services.activities import ActivitiesService


class CategoriesService:
    def __init__(self, db):
        self.categories_repo = CategoriesRepository(db)

        self.activities_service = ActivitiesService(db)

    # ====================== PRIVATE - ACCESSING - CATEGORIES ====================== #

    def _get_categories(
        self,
        current_course_user: CurrentCourseUser,
        course_id: int,
    ) -> list[CategoryResponseDTO]:
        has_activity_view = current_course_user.has_authority("activity_view")
        has_activity_manage = current_course_user.has_authority("activity_manage")
        if not has_activity_view:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to view categories",
            )

        if has_activity_manage:
            categories = self.categories_repo.get_all_categories(course_id)
        else:
            categories = self.categories_repo.get_active_categories(course_id)

        return categories

    # ====================== ACCESSING - CATEGORIES ====================== #

    def get_categories(
        self,
        current_course_user: CurrentCourseUser,
        course_id: int,
    ) -> list[CategoryResponseDTO]:
        return [
            CategoryResponseDTO(
                id=category.id,
                course_id=category.course_id,
                name=category.name,
                description=category.description,
                date_created=category.date_created,
                last_updated=category.last_updated,
                active=category.active,
            )
            for category in self._get_categories(current_course_user, course_id)
        ]

    # ====================== PRIVATE - UTILS ====================== #

    def _clone_all_categories(
        self,
        current_course_user: CurrentCourseUser,
        from_course_id: int,
        to_course_id: int,
    ) -> dict[int, ActivityCategory]:
        categories = self._get_categories(current_course_user, from_course_id)
        for category in categories:
            new_category = self.categories_repo.clone_category(category, to_course_id)
            self.activities_service.clone_all_activities(current_course_user, category, new_category)

    # ====================== MANAGING - CATEGORIES ====================== #

    def create_category(
        self,
        current_course_user: CurrentCourseUser,
        course_id: int,
        category_data: CategoryResponseDTO,
    ) -> CategoryResponseDTO:
        if not current_course_user.has_authority("activity_manage"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to create a category",
            )
        created_category: ActivityCategory = self.categories_repo.create_category(course_id, category_data)
        return CategoryResponseDTO(
            id=created_category.id,
            course_id=created_category.course_id,
            name=created_category.name,
            description=created_category.description,
            date_created=created_category.date_created,
            last_updated=created_category.last_updated,
            active=created_category.active,
        )

    def update_category(
        self,
        current_course_user: CurrentCourseUser,
        course_id: int,
        category_id: int,
        new_category_data: CategoryResponseDTO,
    ) -> CategoryResponseDTO:
        if not current_course_user.has_authority("activity_manage"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to update a category",
            )

        category = self.categories_repo.get_category_by_id_and_course_id(category_id, course_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        self.categories_repo.update_category(new_category_data, category)

        return CategoryResponseDTO(
            id=category.id,
            course_id=category.course_id,
            name=category.name,
            description=category.description,
            date_created=category.date_created,
            last_updated=category.last_updated,
            active=category.active,
        )

    def clone_all_info(
        self,
        current_course_user: CurrentCourseUser,
        from_course_id: int,
        to_course_id: int,
    ) -> None:
        if not current_course_user.has_authority("activity_manage"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to create a category",
            )
        self._clone_all_categories(current_course_user, from_course_id, to_course_id)
