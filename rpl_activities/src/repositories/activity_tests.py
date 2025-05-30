from datetime import datetime, timezone

from rpl_activities.src.dtos.activity_dtos import CreateUnitTestSuiteRequestDTO, IOTestRequestDTO
from rpl_activities.src.dtos.submission_dtos import TestsExecutionLogDTO
from rpl_activities.src.repositories.base import BaseRepository
import sqlalchemy as sa

from rpl_activities.src.repositories.models import aux_models
from rpl_activities.src.repositories.rpl_files import RPLFilesRepository

from .models.activity import Activity
from .models.rpl_file import RPLFile
from .models.unit_test_suite import UnitTestSuite
from .models.io_test import IOTest
from .models.unit_test_run import UnitTestRun
from .models.io_test_run import IOTestRun
from .models.test_execution_log import TestsExecutionLog
from .models.activity_submission import ActivitySubmission

class TestsRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db)
        self.rplfiles_repo = RPLFilesRepository(db)
    
    def get_io_test_by_id_and_activity_id(
        self,
        io_test_id: int,
        activity_id: int
    ) -> IOTest:
        return (
            self.db_session.execute(
                sa.select(IOTest).where(
                    IOTest.id == io_test_id,
                    IOTest.activity_id == activity_id
                )
            )
            .scalars()
            .one_or_none()
        )
    
    def get_unit_test_suite_by_activity_id(
        self,
        activity_id: int
    ) -> UnitTestSuite:
        return (
            self.db_session.execute(
                sa.select(UnitTestSuite).where(
                    UnitTestSuite.activity_id == activity_id
                )
            )
            .scalars()
            .one_or_none()
        )

    def create_io_test_for_activity(
        self,
        new_io_test_data: IOTestRequestDTO,
        activity: Activity
    ) -> IOTest:
        io_test = IOTest(
            activity_id=activity.id,
            name=new_io_test_data.name,
            test_in=new_io_test_data.test_in,
            test_out=new_io_test_data.test_out,
            date_created=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc)
        )
        self.db_session.add(io_test)
        self.db_session.commit()
        return io_test
    
    def update_io_test_for_activity(
        self,
        new_io_test_data: IOTestRequestDTO,
        activity: Activity,
        io_test: IOTest
    ) -> IOTest:
        io_test.name = new_io_test_data.name
        io_test.test_in = new_io_test_data.test_in
        io_test.test_out = new_io_test_data.test_out
        io_test.last_updated = datetime.now(timezone.utc)
        self.db_session.commit()
        self.db_session.refresh(io_test)
        return io_test
    
    def delete_io_test_for_activity(
        self,
        activity: Activity,
        io_test: IOTest
    ) -> Activity:
        self.db_session.delete(io_test)
        self.db_session.commit()
        self.db_session.refresh(activity)
        return activity

    def create_unit_test_suite_for_activity(
        self,
        new_unit_test_suite_data: CreateUnitTestSuiteRequestDTO,
        activity: Activity,
        course_id: int
    ) -> UnitTestSuite:
        rplfile = self.rplfiles_repo.create_rplfile(
            file_name=f"{datetime.today().strftime('%Y-%m-%d')}__{course_id}__{activity.id}__unittests",
            file_type=aux_models.RPLFileType.TEXT,
            data=new_unit_test_suite_data.unit_tests_code.encode()
        )
        unit_test_suite = UnitTestSuite(
            activity_id=activity.id,
            test_rplfile_id=rplfile.id,
            date_created=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc)
        )
        self.db_session.add(unit_test_suite)
        self.db_session.commit()
        self.db_session.refresh(unit_test_suite)
        return unit_test_suite
    
    def update_unit_test_suite_for_activity(
        self,
        new_unit_test_suite_data: CreateUnitTestSuiteRequestDTO,
        activity: Activity,
        course_id: int,
        unit_test_suite: UnitTestSuite
    ) -> UnitTestSuite:
        rplfile = self.rplfiles_repo.update_rplfile(
            rplfile_id=unit_test_suite.test_rplfile_id,
            file_name=f"{datetime.today().strftime('%Y-%m-%d')}__{course_id}__{activity.id}__unittests",
            file_type=aux_models.RPLFileType.TEXT,
            data=new_unit_test_suite_data.unit_tests_code.encode()
        )
        unit_test_suite.test_rplfile_id = rplfile.id
        unit_test_suite.last_updated = datetime.now(timezone.utc)
        self.db_session.commit()
        self.db_session.refresh(unit_test_suite)
        return unit_test_suite

    # ==============================================================================

    def save_tests_execution_log_for_submission(
        self,
        new_execution_log_data: TestsExecutionLogDTO,
        submission: ActivitySubmission
    ) -> tuple[TestsExecutionLog, ActivitySubmission]:
        test_execution_log = TestsExecutionLog(
            activity_submission_id=submission.id,
            success=(new_execution_log_data.tests_execution_result_status == aux_models.TestsExecutionResultStatus.SUCCESS),
            exit_message=new_execution_log_data.tests_execution_exit_message,
            stderr=new_execution_log_data.tests_execution_stderr,
            stdout=new_execution_log_data.tests_execution_stdout,
            date_created=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc)
        )
        self.db_session.add(test_execution_log)
        self.db_session.commit()
        self.db_session.refresh(test_execution_log)
        self.db_session.refresh(submission)
        return test_execution_log, submission

            
                
    

