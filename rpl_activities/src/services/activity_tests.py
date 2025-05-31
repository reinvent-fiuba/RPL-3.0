import logging
from fastapi import HTTPException, status
from rpl_activities.src.deps.auth import CurrentCourseUser
from rpl_activities.src.dtos.activity_dtos import (
    IOTestRequestDTO,
    UnitTestSuiteCreationRequestDTO,
    ActivityResponseDTO,
    IOTestResponseDTO
)
from rpl_activities.src.repositories.activities import ActivitiesRepository
from rpl_activities.src.repositories.activity_tests import TestsRepository
from rpl_activities.src.repositories.models import aux_models
from rpl_activities.src.services.activities import ActivitiesService

class TestsService:
    def __init__(self, db):
        self.tests_repo = TestsRepository(db)
        self.activities_service = ActivitiesService(db)
        self.activities_repo = ActivitiesRepository(db)

    def create_io_test_for_activity(
        self,
        current_course_user: CurrentCourseUser,
        course_id: int,
        activity_id: int,
        new_io_test_data: IOTestRequestDTO
    ) -> IOTestResponseDTO:
        self.activities_service.verify_permission_to_manage(current_course_user)
        activity = self.activities_service.verify_and_get_activity(course_id, activity_id)
        io_test = self.tests_repo.create_io_test_for_activity(new_io_test_data, activity)
        self.activities_repo.enable_iotest_mode_for_activity(activity)
        return IOTestResponseDTO(
            id=io_test.id,
            name=io_test.name,
            test_in=io_test.test_in,
            test_out=io_test.test_out
        )
    

    def update_io_test_for_activity(
        self,
        current_course_user,
        course_id: int,
        activity_id: int,
        io_test_id: int,
        new_io_test_data: IOTestRequestDTO
    ) -> IOTestResponseDTO:
        self.activities_service.verify_permission_to_manage(current_course_user)
        activity = self.activities_service.verify_and_get_activity(course_id, activity_id)
        io_test = self.tests_repo.get_io_test_by_id_and_activity_id(io_test_id, activity.id)
        if not io_test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="IO Test not found"
            )
        io_test = self.tests_repo.update_io_test_for_activity(new_io_test_data, activity, io_test)
        return IOTestResponseDTO(
            id=io_test.id,
            name=io_test.name,
            test_in=io_test.test_in,
            test_out=io_test.test_out
        )
    

    def delete_io_test_for_activity(
        self,
        current_course_user: CurrentCourseUser,
        course_id: int,
        activity_id: int,
        io_test_id: int
    ) -> ActivityResponseDTO:
        self.activities_service.verify_permission_to_manage(current_course_user)
        activity = self.activities_service.verify_and_get_activity(course_id, activity_id)
        io_test = self.tests_repo.get_io_test_by_id_and_activity_id(io_test_id, activity.id)
        if not io_test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="IO Test not found"
            )
        activity = self.tests_repo.delete_io_test_for_activity(activity, io_test)
        return self.activities_service.build_activity_response_dto(activity)


    def create_unit_test_suite_for_activity(
        self,
        current_course_user: CurrentCourseUser,
        course_id: int,
        activity_id: int,
        new_unit_test_data: UnitTestSuiteCreationRequestDTO
    ) -> ActivityResponseDTO:
        self.activities_service.verify_permission_to_manage(current_course_user)
        activity = self.activities_service.verify_and_get_activity(course_id, activity_id)
        unit_test_suite = self.tests_repo.get_unit_test_suite_by_activity_id(activity.id)
        if unit_test_suite:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Unit tests already exists for this activity"
            )
        self.tests_repo.create_unit_test_suite_for_activity(new_unit_test_data, activity, course_id)
        activity = self.activities_repo.disable_iotest_mode_for_activity(activity)
        return self.activities_service.build_activity_response_dto(activity)
        
    
    def update_unit_test_suite_for_activity(
        self,
        current_course_user: CurrentCourseUser,
        course_id: int,
        activity_id: int,
        new_unit_test_data: UnitTestSuiteCreationRequestDTO
    ) -> ActivityResponseDTO:
        self.activities_service.verify_permission_to_manage(current_course_user)
        activity = self.activities_service.verify_and_get_activity(course_id, activity_id)
        unit_test_suite = self.tests_repo.get_unit_test_suite_by_activity_id(activity.id)
        if not unit_test_suite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unit tests not found"
            )
        self.tests_repo.update_unit_test_suite_for_activity(new_unit_test_data, activity, course_id, unit_test_suite)
        return self.activities_service.build_activity_response_dto(activity)