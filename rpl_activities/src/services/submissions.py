import logging
from fastapi import HTTPException, status
from rpl_activities.src.deps.auth import CurrentCourseUser
from rpl_activities.src.dtos.submission_dtos import (
    SubmissionCreationRequestDTO,
    AllFinalSubmissionsResponseDTO,
    SubmissionResultResponseDTO,
    SubmissionResponseDTO,
    UpdateSubmissionStatusRequestDTO,
    TestSuiteDTO,
    UnitTestsResultsDTO,
    SubmissionResultCreationDTO,
    SubmissionWithMetadataOnlyResponseDTO
)
from rpl_activities.src.repositories.submissions import SubmissionsRepository
from rpl_activities.src.repositories.activities import ActivitiesRepository
from rpl_activities.src.repositories.models import aux_models
from rpl_activities.src.repositories.models.activity import Activity
from rpl_activities.src.repositories.models.activity_submission import ActivitySubmission
from rpl_activities.src.services.activities import ActivitiesService


class SubmissionsService:
    def __init__(self, db_session):
        self.submissions_repo = SubmissionsRepository(db_session)
        # self.activities_repo = ActivitiesRepository(db_session)
        self.activities_service = ActivitiesService(db_session)


    def __build_submission_response(
        self,
        submission: ActivitySubmission,
    ) -> SubmissionResponseDTO:
        return SubmissionResponseDTO(
            id=submission.id,
            submission_rplfile_name=submission.response_rplfile.file_name,
            submission_rplfile_type=submission.response_rplfile.file_type,
            submission_rplfile_id=submission.response_rplfile_id,
            acitivity_starting_rplfile_name=submission.activity.starting_rplfile.file_name,
            activity_starting_rplfile_type=submission.activity.starting_rplfile.file_type,
            activity_starting_rplfile_id=submission.activity.starting_rplfile_id,
            activity_language=submission.activity.language,
            is_io_tested=submission.activity.is_io_tested,
            compilation_flags=submission.activity.compilation_flags,
            activity_unit_tests_content=submission.activity.unit_test.test_rplfile.data.decode() if submission.activity.unit_test else "",
            activity_io_tests_input=[iotest.test_in for iotest in submission.activity.io_tests]
        )
    
    def __build_submission_with_metadata_only_response(
        self,
        submission: ActivitySubmission,
    ) -> SubmissionWithMetadataOnlyResponseDTO:
        return SubmissionWithMetadataOnlyResponseDTO(
            id=submission.id,
            submission_rplfile_name=submission.response_rplfile.file_name,
            submission_rplfile_type=submission.response_rplfile.file_type,
            submission_rplfile_id=submission.response_rplfile_id,
            acitivity_starting_rplfile_name=submission.activity.starting_rplfile.file_name,
            activity_starting_rplfile_type=submission.activity.starting_rplfile.file_type,
            activity_starting_rplfile_id=submission.activity.starting_rplfile_id,
            activity_language=submission.activity.language,
            is_io_tested=submission.activity.is_io_tested
        )
    
    def __verify_and_get_submission(
        self,
        submission_id: int
    ) -> ActivitySubmission:
        submission = self.submissions_repo.get_by_id(submission_id)
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Submission with id {submission_id} not found."
            )
        return submission


    # ==============================================================================

    def get_submission(self, submission_id: int) -> SubmissionResponseDTO:
        submission = self.__verify_and_get_submission(submission_id)
        return self.__build_submission_response(submission)
    

    def create_submission(
        self,
        course_id: int,
        activity_id: int,
        new_submission_data: SubmissionCreationRequestDTO,
        current_course_user: CurrentCourseUser
    ) -> SubmissionWithMetadataOnlyResponseDTO:
        self.activities_service.verify_permission_to_submit(current_course_user)
        activity = self.activities_service.verify_and_get_activity(course_id, activity_id)
        submission = self.submissions_repo.create_submission_for_activity(new_submission_data, activity, current_course_user)
        return self.__build_submission_with_metadata_only_response(submission)
    
    
    def update_submission_status(
        self,
        submission_id: int,
        new_status_data: UpdateSubmissionStatusRequestDTO
    ) -> SubmissionWithMetadataOnlyResponseDTO:
        submission = self.__verify_and_get_submission(submission_id)
        updated_submission = self.submissions_repo.update_submission_status(submission, new_status_data)
        return self.__build_submission_with_metadata_only_response(updated_submission)
    

    def mark_submission_as_final_solution(
        self,
        course_id: int,
        activity_id: int,
        submission_id: int,
        current_course_user: CurrentCourseUser
    ) -> SubmissionWithMetadataOnlyResponseDTO:
        self.activities_service.verify_permission_to_submit(current_course_user)
        submission = self.__verify_and_get_submission(submission_id)      
        updated_submission = self.submissions_repo.mark_submission_as_final_solution(submission)
        return self.__build_submission_with_metadata_only_response(updated_submission)


    def get_final_submission_for_current_student(
        self,
        course_id: int,
        activity_id: int,
        current_course_user: CurrentCourseUser
    ) -> SubmissionWithMetadataOnlyResponseDTO:
        self.activities_service.verify_permission_to_submit(current_course_user)
        final_submission = self.submissions_repo.get_final_submission_by_current_user_from_activity(
            activity_id,
            current_course_user
        )
        if not final_submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Final submission not found for the current user."
            )
        return self.__build_submission_with_metadata_only_response(final_submission)




