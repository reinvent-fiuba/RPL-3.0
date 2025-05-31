import logging
from typing import Union
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from rpl_activities.src.deps.auth import CurrentCourseUser
from rpl_activities.src.dtos.submission_dtos import (
    IOTestRunResultDTO,
    SubmissionCreationRequestDTO,
    AllFinalSubmissionsResponseDTO,
    SubmissionResultResponseDTO,
    SubmissionResponseDTO,
    UnitTestRunResultDTO,
    UpdateSubmissionStatusRequestDTO,
    SingleUnitTestRunReportDTO,
    UnitTestSuiteRunsSummaryDTO,
    TestsExecutionLogDTO,
    SubmissionWithMetadataOnlyResponseDTO
)
from rpl_activities.src.repositories.activity_tests import TestsRepository
from rpl_activities.src.repositories.submissions import SubmissionsRepository
from rpl_activities.src.repositories.activities import ActivitiesRepository
from rpl_activities.src.repositories.models import aux_models
from rpl_activities.src.repositories.models.activity import Activity
from rpl_activities.src.repositories.models.activity_submission import ActivitySubmission
from rpl_activities.src.services.activities import ActivitiesService


class SubmissionsService:
    def __init__(self, db_session):
        self.submissions_repo = SubmissionsRepository(db_session)
        self.tests_repo = TestsRepository(db_session)
        # self.activities_repo = ActivitiesRepository(db_session)
        self.activities_service = ActivitiesService(db_session)


    def __build_submission_response(
        self,
        submission: ActivitySubmission,
    ) -> SubmissionResponseDTO:
        unit_tests_data = self.submissions_repo.get_unit_tests_data_from_submission(submission)
        io_tests_input_data = self.submissions_repo.get_io_tests_input_data_from_submission(submission)
        return SubmissionResponseDTO(
            id=submission.id,
            submission_rplfile_name=submission.solution_rplfile.file_name,
            submission_rplfile_type=submission.solution_rplfile.file_type,
            submission_rplfile_id=submission.solution_rplfile_id,
            acitivity_starting_rplfile_name=submission.activity.starting_rplfile.file_name,
            activity_starting_rplfile_type=submission.activity.starting_rplfile.file_type,
            activity_starting_rplfile_id=submission.activity.starting_rplfile_id,
            activity_language=submission.activity.language,
            is_io_tested=submission.activity.is_io_tested,
            compilation_flags=submission.activity.compilation_flags,
            activity_unit_tests_content=unit_tests_data,
            activity_io_tests_input=io_tests_input_data
        )
    
    def __build_submission_with_metadata_only_response(
        self,
        submission: ActivitySubmission,
    ) -> SubmissionWithMetadataOnlyResponseDTO:
        return SubmissionWithMetadataOnlyResponseDTO(
            id=submission.id,
            submission_rplfile_name=submission.solution_rplfile.file_name,
            submission_rplfile_type=submission.solution_rplfile.file_type,
            submission_rplfile_id=submission.solution_rplfile_id,
            activity_starting_rplfile_name=submission.activity.starting_rplfile.file_name,
            activity_starting_rplfile_type=submission.activity.starting_rplfile.file_type,
            activity_starting_rplfile_id=submission.activity.starting_rplfile_id,
            activity_language=submission.activity.language,
            is_io_tested=submission.activity.is_io_tested
        )

    def __build_submission_result_response(
        self,
        submission: ActivitySubmission
    ) -> SubmissionResultResponseDTO:
        unit_tests_data = self.submissions_repo.get_unit_tests_data_from_submission(submission)
        io_tests_input_data = self.submissions_repo.get_io_tests_input_data_from_submission(submission)
        submission_tests_exit_msg = self.submissions_repo.get_tests_exit_msg_from_submission(submission)
        io_tests_run_results = self.submissions_repo.get_io_tests_run_results_from_submission(submission)
        unit_tests_run_results = self.submissions_repo.get_unit_tests_run_results_from_submission(submission)
        return SubmissionResultResponseDTO(
            id=submission.id,
            activity_id=submission.activity_id,
            submission_rplfile_name=submission.solution_rplfile.file_name,
            submission_rplfile_type=submission.solution_rplfile.file_type,
            submission_rplfile_id=submission.solution_rplfile_id,
            acitivity_starting_rplfile_name=submission.activity.starting_rplfile.file_name,
            activity_starting_rplfile_type=submission.activity.starting_rplfile.file_type,
            activity_starting_rplfile_id=submission.activity.starting_rplfile_id,
            activity_language=submission.activity.language,
            is_io_tested=submission.activity.is_io_tested,
            activity_unit_tests_content=unit_tests_data,
            activity_io_tests_input=io_tests_input_data,
            submission_status=submission.status,
            is_final_solution=submission.is_final_solution,
            submission_date=submission.date_created,
            exit_message=submission_tests_exit_msg,
            iotests_run_results=io_tests_run_results,
            unittests_run_results=unit_tests_run_results
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


    def __set_submission_status_according_to_tests_exec_log(
        self,
        submission: ActivitySubmission,
        new_execution_log_data: TestsExecutionLogDTO,
        passed_all_tests: bool
    ):  
        if new_execution_log_data.tests_execution_result_status == aux_models.TestsExecutionResultStatus.TIME_OUT:
            submission = self.submissions_repo.update_submission_status(
                submission,
                aux_models.SubmissionStatus.TIME_OUT
            )
        elif passed_all_tests:
            submission = self.submissions_repo.update_submission_status(
                submission,
                aux_models.SubmissionStatus.SUCCESS
            )
        else:
            submission = self.submissions_repo.update_submission_status(
                submission,
                aux_models.SubmissionStatus.FAILURE
            )

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
        # TODO self.post_submission_to_queue
        return self.__build_submission_with_metadata_only_response(submission)
    
    
    def update_submission_status(
        self,
        submission_id: int,
        new_status_data: UpdateSubmissionStatusRequestDTO
    ) -> SubmissionWithMetadataOnlyResponseDTO:
        submission = self.__verify_and_get_submission(submission_id)
        updated_submission = self.submissions_repo.update_submission_status(submission, new_status_data.status)
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


    def get_all_final_submissions_from_activity(
        self,
        course_id: int,
        activity_id: int,
        current_course_user: CurrentCourseUser
    ) -> AllFinalSubmissionsResponseDTO:
        self.activities_service.verify_permission_to_submit(current_course_user)
        final_submissions = self.submissions_repo.get_all_final_submissions_for_activity(activity_id)
        if not final_submissions:
            return AllFinalSubmissionsResponseDTO(submission_rplfile_ids=[])
        submission_rplfile_ids = [submission.solution_rplfile_id for submission in final_submissions]
        return AllFinalSubmissionsResponseDTO(submission_rplfile_ids=submission_rplfile_ids)
    

    def save_tests_execution_log_for_submission(
        self,
        submission_id: int,
        new_execution_log_data: TestsExecutionLogDTO
    ):
        submission = self.__verify_and_get_submission(submission_id)
        test_execution_log, submission = self.tests_repo.save_tests_execution_log_for_submission(
            new_execution_log_data,
            submission
        )
        if new_execution_log_data.tests_execution_result_status == aux_models.TestsExecutionResultStatus.ERROR:
            submission = self.submissions_repo.update_submission_status(
                submission,
                aux_models.SubmissionStatus.from_tests_execution_errored_stage(
                    new_execution_log_data.tests_execution_stage
                )
            )
            return
        
        passed_all_tests = False
        if submission.activity.is_io_tested:
            passed_all_tests = self.tests_repo.save_io_test_runs_from_exec_log_and_check_if_all_passed(
                submission.activity.io_tests, 
                test_execution_log.id, 
                new_execution_log_data
            )
        elif submission.activity.unit_test_suite:
            passed_all_tests = self.tests_repo.save_unit_test_runs_from_exec_log_and_check_if_all_passed(
                test_execution_log.id,
                new_execution_log_data
            )
        self.__set_submission_status_according_to_tests_exec_log(
            submission,
            new_execution_log_data,
            passed_all_tests
        )


    def get_submission_execution_result(
        self,
        submission_id: int
    ) -> SubmissionResultResponseDTO:
        submission = self.__verify_and_get_submission(submission_id)
        if submission.status in [
            aux_models.SubmissionStatus.PENDING,
            aux_models.SubmissionStatus.ENQUEUED,
            aux_models.SubmissionStatus.PROCESSING
        ]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"submission_status: {submission.status}"
            )
        return self.__build_submission_result_response(submission)
        
        
        

        

        

        


