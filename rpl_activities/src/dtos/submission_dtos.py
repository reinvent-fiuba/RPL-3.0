from datetime import datetime
from typing import List, Optional
from fastapi import File, UploadFile
from pydantic import BaseModel

from rpl_activities.src.repositories.models import aux_models


# ==============================================================================
# User-facing DTOs


class SubmissionCreationRequestDTO(BaseModel):
    description: Optional[List[str]] = None
    file: List[UploadFile] = File(...)
    model_config = {"extra": "forbid"}


class AllFinalSubmissionsResponseDTO(BaseModel):
    submission_rplfile_ids: List[int]


class IOTestRunResult(BaseModel):
    name: str
    test_in: str
    expected_output: str
    run_output: str

class UnitTestRunResult(BaseModel):
    name: str
    passed: bool
    error_messages: Optional[str] = None

class SubmissionResultResponseDTO(BaseModel):
    id: int
    activity_id: int
    submission_rplfile_name: str
    submission_rplfile_type: aux_models.RPLFileType
    submission_rplfile_id: int
    acitivity_starting_rplfile_name: str
    activity_starting_rplfile_type: aux_models.RPLFileType
    activity_starting_rplfile_id: int
    activity_language: aux_models.LanguageWithVersion
    is_io_tested: bool
    activity_unit_tests_content: str = ""
    activity_io_tests_input: List[str] = []
    submission_status: aux_models.SubmissionStatus
    is_final_solution: bool
    submission_date: datetime
    exit_message: str
    iotests_run_results: Optional[List[IOTestRunResult]] = None
    unittests_run_results: Optional[List[UnitTestRunResult]] = None


# ==============================================================================
# Runner-facing DTOs


class SubmissionResponseDTO(BaseModel):
    id: int
    submission_rplfile_name: str
    submission_rplfile_type: aux_models.RPLFileType
    submission_rplfile_id: int
    acitivity_starting_rplfile_name: str
    activity_starting_rplfile_type: aux_models.RPLFileType
    activity_starting_rplfile_id: int
    activity_language: aux_models.LanguageWithVersion
    is_io_tested: bool
    compilation_flags: str = ""
    activity_unit_tests_content: str = ""
    activity_io_tests_input: List[str] = []

class UpdateSubmissionStatusRequestDTO(BaseModel):
    status: aux_models.SubmissionStatus


class TestSuiteDTO(BaseModel):
    name: str
    status: str
    messages: str

class UnitTestsResultsDTO(BaseModel):
    passed: int
    failed: int
    errored: int
    tests: List[TestSuiteDTO]

class SubmissionResultCreationDTO(BaseModel):
    test_run_result: str
    test_run_stage: str
    test_run_exit_message: str
    test_run_stderr: str
    test_run_stdout: str
    test_run_unit_test_result: UnitTestsResultsDTO


# ==============================================================================
# Used by both


class SubmissionWithMetadataOnlyResponseDTO(BaseModel):
    id: int
    submission_rplfile_name: str
    submission_rplfile_type: aux_models.RPLFileType
    submission_rplfile_id: int
    acitivity_starting_rplfile_name: str
    activity_starting_rplfile_type: aux_models.RPLFileType
    activity_starting_rplfile_id: int
    activity_language: aux_models.LanguageWithVersion
    is_io_tested: bool

