from typing import List, Optional
from fastapi import APIRouter, Form, status
from rpl_activities.src.deps.auth import CurrentCourseUserDependency

from rpl_activities.src.deps.database import DBSessionDependency
from rpl_activities.src.dtos.activity_dtos import ActivityCreationRequestDTO, ActivityResponseDTO, ActivityUpdateRequestDTO, ActivityWithMetadataOnlyResponseDTO
from rpl_activities.src.services.activities import ActivitiesService



router = APIRouter(prefix="/api/v3", tags=["Activities"])

# ==============================================================================

@router.get("/courses/{course_id}/activities", response_model=List[ActivityWithMetadataOnlyResponseDTO])
def get_all_activities(
    course_id: int,
    current_course_user: CurrentCourseUserDependency,
    db: DBSessionDependency,
):
    return ActivitiesService(db).get_all_activities_for_current_user(current_course_user, course_id)


@router.get("/courses/{course_id}/activities/{activity_id}", response_model=ActivityResponseDTO)
def get_activity(
    course_id: int,
    activity_id: int,
    current_course_user: CurrentCourseUserDependency,
    db: DBSessionDependency,
):
    return ActivitiesService(db).get_activity(current_course_user, course_id, activity_id)


@router.delete("/courses/{course_id}/activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(
    course_id: int,
    activity_id: int,
    current_course_user: CurrentCourseUserDependency,
    db: DBSessionDependency,
):
    ActivitiesService(db).delete_activity(current_course_user, course_id, activity_id)


@router.post("/courses/{course_id}/activities", response_model=ActivityResponseDTO, status_code=status.HTTP_201_CREATED)
def create_activity(
    course_id: int,
    current_course_user: CurrentCourseUserDependency,
    db: DBSessionDependency,
    new_activity_data: ActivityCreationRequestDTO = Form(..., media_type="multipart/form-data")
):
    return ActivitiesService(db).create_activity(current_course_user, course_id, new_activity_data)


@router.patch("/courses/{course_id}/activities/{activity_id}", response_model=ActivityResponseDTO)
def update_activity(
    course_id: int,
    activity_id: int,
    current_course_user: CurrentCourseUserDependency,
    db: DBSessionDependency,
    new_activity_data: ActivityUpdateRequestDTO = Form(..., media_type="multipart/form-data")
):
    return ActivitiesService(db).update_activity(current_course_user, course_id, activity_id, new_activity_data)
