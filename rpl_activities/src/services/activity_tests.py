import logging
from fastapi import HTTPException, status
from rpl_activities.src.deps.auth import CurrentCourseUser
from rpl_activities.src.dtos.activity_dtos import (
    IOTestRequestDTO,
    UnitTestSuiteCreationRequestDTO,
    ActivityResponseDTO,
    IOTestResponseDTO,
)
from rpl_activities.src.repositories.activities import ActivitiesRepository
from rpl_activities.src.repositories.activity_tests import TestsRepository
from rpl_activities.src.repositories.models import aux_models
from rpl_activities.src.repositories.models.activity import Activity


class TestsService:
    def __init__(self, db):
        self.tests_repo = TestsRepository(db)
        self.activities_repo = ActivitiesRepository(db)

    # ====================== PRIVATE - PERMISSIONS ====================== #

    def _verify_permission_to_manage(self, current_course_user: CurrentCourseUser):
        can_manage_activities = current_course_user.has_authority("activity_manage")
        if not can_manage_activities:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to manage activities on this course",
            )

    def _verify_and_get_activity(self, course_id: int, activity_id: int) -> Activity:
        activity = self.activities_repo.get_activity_by_id(activity_id)
        if not activity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
        if activity.course_id != course_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Activity does not belong to the course"
            )
        return activity

    def _build_activity_response_dto(self, activity: Activity) -> ActivityResponseDTO:
        unit_tests_data = self.activities_repo.get_unit_tests_data_from_activity(activity)
        io_tests_data = self.activities_repo.get_io_tests_data_from_activity(activity)
        return ActivityResponseDTO(
            id=activity.id,
            course_id=activity.course_id,
            category_id=activity.category_id,
            category_name=activity.category.name,
            category_description=activity.category.description,
            name=activity.name,
            description=activity.description,
            language=aux_models.LanguageWithVersion(activity.language).without_version(),
            is_io_tested=activity.is_io_tested,
            active=activity.active,
            deleted=activity.deleted,
            points=activity.points,
            starting_rplfile_id=activity.starting_rplfile.id,
            activity_unittests=unit_tests_data,
            activity_iotests=io_tests_data,
            compilation_flags=activity.compilation_flags,
            date_created=activity.date_created,
            last_updated=activity.last_updated,
        )

    # ====================== MANAGING - IO TESTS ====================== #

    def create_io_test_for_activity(
        self,
        current_course_user: CurrentCourseUser,
        course_id: int,
        activity_id: int,
        new_io_test_data: IOTestRequestDTO,
    ) -> IOTestResponseDTO:
        self._verify_permission_to_manage(current_course_user)
        activity = self._verify_and_get_activity(course_id, activity_id)
        io_test = self.tests_repo.create_io_test_for_activity(new_io_test_data, activity)
        self.activities_repo.enable_iotest_mode_for_activity(activity)
        return IOTestResponseDTO(
            id=io_test.id, name=io_test.name, test_in=io_test.test_in, test_out=io_test.test_out
        )

    def update_io_test_for_activity(
        self,
        current_course_user,
        course_id: int,
        activity_id: int,
        io_test_id: int,
        new_io_test_data: IOTestRequestDTO,
    ) -> IOTestResponseDTO:
        self._verify_permission_to_manage(current_course_user)
        activity = self._verify_and_get_activity(course_id, activity_id)
        io_test = self.tests_repo.get_io_test_by_id_and_activity_id(io_test_id, activity.id)
        if not io_test:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IO Test not found")
        io_test = self.tests_repo.update_io_test_for_activity(new_io_test_data, activity, io_test)
        return IOTestResponseDTO(
            id=io_test.id, name=io_test.name, test_in=io_test.test_in, test_out=io_test.test_out
        )

    def delete_io_test_for_activity(
        self, current_course_user: CurrentCourseUser, course_id: int, activity_id: int, io_test_id: int
    ) -> ActivityResponseDTO:
        self._verify_permission_to_manage(current_course_user)
        activity = self._verify_and_get_activity(course_id, activity_id)
        io_test = self.tests_repo.get_io_test_by_id_and_activity_id(io_test_id, activity.id)
        if not io_test:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IO Test not found")
        activity = self.tests_repo.delete_io_test_for_activity(activity, io_test)
        return self._build_activity_response_dto(activity)

    # ====================== MANAGING - UNIT TEST SUITE ====================== #

    def create_unit_test_suite_for_activity(
        self,
        current_course_user: CurrentCourseUser,
        course_id: int,
        activity_id: int,
        new_unit_test_data: UnitTestSuiteCreationRequestDTO,
    ) -> ActivityResponseDTO:
        self._verify_permission_to_manage(current_course_user)
        activity = self._verify_and_get_activity(course_id, activity_id)
        unit_test_suite = self.tests_repo.get_unit_test_suite_by_activity_id(activity.id)
        if unit_test_suite:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Unit tests already exists for this activity"
            )
        self.tests_repo.create_unit_test_suite_for_activity(new_unit_test_data, activity, course_id)
        activity = self.activities_repo.disable_iotest_mode_for_activity(activity)
        return self._build_activity_response_dto(activity)

    def update_unit_test_suite_for_activity(
        self,
        current_course_user: CurrentCourseUser,
        course_id: int,
        activity_id: int,
        new_unit_test_data: UnitTestSuiteCreationRequestDTO,
    ) -> ActivityResponseDTO:
        self._verify_permission_to_manage(current_course_user)
        activity = self._verify_and_get_activity(course_id, activity_id)
        unit_test_suite = self.tests_repo.get_unit_test_suite_by_activity_id(activity.id)
        if not unit_test_suite:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit tests not found")
        self.tests_repo.update_unit_test_suite_for_activity(
            new_unit_test_data, activity, course_id, unit_test_suite
        )
        return self._build_activity_response_dto(activity)

    # ====================== MANAGING - ALL TESTS ====================== #

    def clone_all_activity_tests(
        self, current_course_user: CurrentCourseUser, from_activity: Activity, to_activity: Activity
    ):
        self._verify_permission_to_manage(current_course_user)
        if from_activity.is_io_tested:
            io_tests = self.tests_repo.get_all_io_tests_by_activity_id(from_activity.id)
            for io_test in io_tests:
                self.tests_repo.clone_io_test(io_test, to_activity)
        else:
            unit_test_suite = self.tests_repo.get_unit_test_suite_by_activity_id(from_activity.id)
            if unit_test_suite is not None:
                self.tests_repo.clone_unit_test_suite(unit_test_suite, to_activity)
