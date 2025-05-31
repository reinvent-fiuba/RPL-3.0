from typing import List, Optional
from fastapi import APIRouter, Form, status
from rpl_activities.src.deps.auth import CurrentCourseUserDependency
from rpl_activities.src.deps.database import DBSessionDependency
from rpl_activities.src.dtos.activity_dtos import (
    IOTestRequestDTO,
    UnitTestSuiteCreationRequestDTO,
    ActivityResponseDTO,
    IOTestResponseDTO
)
from rpl_activities.src.services.activity_tests import TestsService



router = APIRouter(prefix="/api/v3", tags=["Activity Tests"])

# ==============================================================================


@router.post(
    "/courses/{course_id}/activities/{activity_id}/iotests",
    response_model=IOTestResponseDTO,
    status_code=status.HTTP_201_CREATED
)
def create_io_test_case(
    course_id: int,
    activity_id: int,
    new_io_test_data: IOTestRequestDTO,
    db: DBSessionDependency,
    current_course_user: CurrentCourseUserDependency
):
    return TestsService(db).create_io_test_for_activity(current_course_user, course_id, activity_id, new_io_test_data)


@router.put(
    "/courses/{course_id}/activities/{activity_id}/iotests/{io_test_id}",
    response_model=IOTestResponseDTO,
)
def update_io_test_case(
    course_id: int,
    activity_id: int,
    io_test_id: int,
    new_io_test_data: IOTestRequestDTO,
    db: DBSessionDependency,
    current_course_user: CurrentCourseUserDependency
):
    return TestsService(db).update_io_test_for_activity(current_course_user, course_id, activity_id, io_test_id, new_io_test_data)


@router.delete(
    "/courses/{course_id}/activities/{activity_id}/iotests/{io_test_id}",
    response_model=ActivityResponseDTO,
)
def delete_io_test_case(
    course_id: int,
    activity_id: int,
    io_test_id: int,
    db: DBSessionDependency,
    current_course_user: CurrentCourseUserDependency
):
    return TestsService(db).delete_io_test_for_activity(current_course_user, course_id, activity_id, io_test_id)


@router.post(
    "/courses/{course_id}/activities/{activity_id}/unittests",
    response_model=ActivityResponseDTO,
    status_code=status.HTTP_201_CREATED
)
def create_unit_tests(
    course_id: int,
    activity_id: int,
    new_unit_tests_data: UnitTestSuiteCreationRequestDTO,
    db: DBSessionDependency,
    current_course_user: CurrentCourseUserDependency
):
    return TestsService(db).create_unit_test_suite_for_activity(current_course_user, course_id, activity_id, new_unit_tests_data)


@router.put(
    "/courses/{course_id}/activities/{activity_id}/unittests",
    response_model=ActivityResponseDTO,
)
def update_unit_tests(
    course_id: int,
    activity_id: int,
    new_unit_tests_data: UnitTestSuiteCreationRequestDTO,
    db: DBSessionDependency,
    current_course_user: CurrentCourseUserDependency
):
    return TestsService(db).update_unit_test_suite_for_activity(current_course_user, course_id, activity_id, new_unit_tests_data)
