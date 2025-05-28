from datetime import datetime, timezone

from rpl_activities.src.dtos.activity_dtos import CreateUnitTestRequestDTO, IOTestRequestDTO
from rpl_activities.src.repositories.base import BaseRepository
import sqlalchemy as sa

from rpl_activities.src.repositories.models import aux_models
from rpl_activities.src.repositories.rpl_files import RPLFilesRepository

from .models.activity import Activity
from .models.rpl_file import RPLFile
from .models.unit_test import UnitTest
from .models.io_test import IOTest

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
    
    def get_unit_test_by_activity_id(
        self,
        activity_id: int
    ) -> UnitTest:
        return (
            self.db_session.execute(
                sa.select(UnitTest).where(
                    UnitTest.activity_id == activity_id
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

    def create_unit_test_for_activity(
        self,
        new_unit_test_data: CreateUnitTestRequestDTO,
        activity: Activity,
        course_id: int
    ) -> UnitTest:
        rplfile = self.rplfiles_repo.create_rplfile(
            file_name=f"{datetime.today().strftime('%Y-%m-%d')}__{course_id}__{activity.id}__unittests",
            file_type=aux_models.RPLFileType.TEXT,
            data=new_unit_test_data.unit_test_code.encode()
        )
        unit_test = UnitTest(
            activity_id=activity.id,
            test_rplfile_id=rplfile.id,
            date_created=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc)
        )
        self.db_session.add(unit_test)
        self.db_session.commit()
        self.db_session.refresh(unit_test)
        return unit_test
    
    def update_unit_test_for_activity(
        self,
        new_unit_test_data: CreateUnitTestRequestDTO,
        activity: Activity,
        course_id: int,
        unit_test: UnitTest
    ) -> UnitTest:
        rplfile = self.rplfiles_repo.update_rplfile(
            rplfile_id=unit_test.test_rplfile_id,
            file_name=f"{datetime.today().strftime('%Y-%m-%d')}__{course_id}__{activity.id}__unittests",
            file_type=aux_models.RPLFileType.TEXT,
            data=new_unit_test_data.unit_test_code.encode()
        )
        unit_test.test_rplfile_id = rplfile.id
        unit_test.last_updated = datetime.now(timezone.utc)
        self.db_session.commit()
        self.db_session.refresh(unit_test)
        return unit_test

        
    

