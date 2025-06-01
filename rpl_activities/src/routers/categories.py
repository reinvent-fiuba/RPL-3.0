from typing import List, Optional
from fastapi import APIRouter, status
from rpl_activities.src.deps.auth import CurrentMainUserDependency
from rpl_activities.src.deps.auth import CurrentCourseUserDependency

from rpl_activities.src.deps.database import DBSessionDependency
from rpl_activities.src.dtos.category_dtos import (
    CategoryCreationRequestDTO,
    CategoryResponseDTO,
    CategoryUpdateRequestDTO,
)
from rpl_activities.src.services.categories import CategoriesService


router = APIRouter(prefix="/api/v3", tags=["ActivityCategories"])

# ==============================================================================


@router.get(
    "/courses/{course_id}/activityCategories", response_model=List[CategoryResponseDTO]
)
def get_categories(
    course_id: int,
    current_course_user: CurrentCourseUserDependency,
    db: DBSessionDependency,
):
    return CategoriesService(db).get_categories(current_course_user, course_id)


@router.post(
    "/courses/{course_id}/activityCategories",
    status_code=status.HTTP_201_CREATED,
    response_model=CategoryResponseDTO,
)
def create_category(
    course_id: int,
    category_data: CategoryCreationRequestDTO,
    current_course_user: CurrentCourseUserDependency,
    db: DBSessionDependency,
):
    return CategoriesService(db).create_category(
        current_course_user,
        course_id,
        category_data,
    )


@router.patch(
    "/courses/{course_id}/activityCategories/{category_id}",
    response_model=CategoryResponseDTO,
)
def update_category(
    course_id: int,
    category_id: int,
    new_category_data: CategoryUpdateRequestDTO,
    current_course_user: CurrentCourseUserDependency,
    db: DBSessionDependency,
):
    return CategoriesService(db).update_category(
        current_course_user,
        course_id,
        category_id,
        new_category_data,
    )


# ==============================================================================


@router.post(
    "/courses/{from_course_id}/activityCategories/clone",
    status_code=status.HTTP_201_CREATED,
)
def clone_all_info(
    from_course_id: int,
    current_course_user: CurrentCourseUserDependency,
    db: DBSessionDependency,
    to_course_id=int,
):
    return CategoriesService(db).clone_all_info(
        current_course_user, from_course_id, to_course_id
    )
