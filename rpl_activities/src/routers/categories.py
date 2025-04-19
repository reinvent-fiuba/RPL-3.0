from typing import Optional
from fastapi import APIRouter, status
from rpl_activities.src.deps.auth import CurrentMainUserDependency
from rpl_activities.src.deps.auth import CurrentCourseUserDependency

from rpl_activities.src.deps.database import DBSessionDependency
from rpl_activities.src.dtos.category_dtos import CategoryCreationDTO
from rpl_activities.src.services.categories import CategoriesService


router = APIRouter(prefix="/api/v3", tags=["ActivityCategories"])


@router.post(
    "/courses/{course_id}/categories",
    status_code=status.HTTP_201_CREATED,
    response_model=CategoryCreationDTO,
)
def create_category(
    course_id: int,
    category_data: CategoryCreationDTO,
    current_course_user: CurrentCourseUserDependency,
    db: DBSessionDependency,
) -> CategoryCreationDTO:
    return CategoriesService(db).create_category(
        current_course_user=current_course_user,
        course_id=course_id,
        category_data=category_data,
    )
