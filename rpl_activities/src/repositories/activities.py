from datetime import datetime, timezone
import logging
from typing import Optional

from rpl_activities.src.deps import tar_utils
from rpl_activities.src.dtos.activity_dtos import ActivityCreationRequestDTO, ActivityUpdateRequestDTO, IOTestDTO
from rpl_activities.src.repositories.base import BaseRepository
import sqlalchemy as sa

from rpl_activities.src.repositories.models import aux_models
from rpl_activities.src.repositories.rpl_files import RPLFilesRepository
from .models.activity import Activity

class ActivitiesRepository(BaseRepository):
    def __init__(self, db_session):
        super().__init__(db_session)
        self.rplfiles_repo = RPLFilesRepository(db_session)

    def get_all_activities_by_course_id(self, course_id: int):
        return (
            self.db_session.execute(
                sa.select(Activity).where(
                    Activity.course_id == course_id,
                    Activity.deleted == False,
                )
            )
            .scalars()
            .all()
        )

    def get_all_active_activities_by_course_id(self, course_id: int):
        return (
            self.db_session.execute(
                sa.select(Activity).where(
                    Activity.course_id == course_id,
                    Activity.deleted == False,
                    Activity.active == True,
                )
            )
            .scalars()
            .all()
        )

    def get_activity_by_id(self, activity_id: int):
        return (
            self.db_session.execute(
                sa.select(Activity).where(
                    Activity.id == activity_id,
                    Activity.deleted == False,
                )
            )
            .scalars()
            .one_or_none()
        )
    
    def get_unit_tests_data(self, activity: Activity) -> str:
        return activity.unit_test.test_rplfile.data.decode() if activity.unit_test else ""
    
    def get_io_tests_data(self, activity: Activity) -> list[IOTestDTO]:
        io_tests = activity.io_tests
        return [
            IOTestDTO(
                name=io_test.name,
                test_in=io_test.test_in,
                test_out=io_test.test_out,
            )
            for io_test in io_tests
        ] if io_tests else []
    
    def delete_activity(self, activity: Activity):
        activity.deleted = True
        activity.last_updated = datetime.now(timezone.utc)
        self.db_session.commit()

    def create_activity(
        self,
        course_id: int,
        new_activity_data: ActivityCreationRequestDTO
    ) -> Activity:
        compressed_rplfile_bytes = tar_utils.compress_files_to_tar_gz(
            new_activity_data.starting_files
        )
        rplfile = self.rplfiles_repo.create_rplfile(
            file_name=datetime.today().strftime("%Y-%m-%d") + ".tar.gz",
            file_type="application/gzip",
            data=compressed_rplfile_bytes,
        )

        if (new_activity_data.compilation_flags is None) and (new_activity_data.language == aux_models.Language.C):
            new_activity_data.compilation_flags = aux_models.DEFAULT_GCC_FLAGS
                
        activity = Activity(
            course_id=course_id,
            category_id=new_activity_data.category_id,
            name=new_activity_data.name,
            description=new_activity_data.description,
            language=new_activity_data.language.with_version(),
            is_io_tested=False,
            active=new_activity_data.active,
            deleted=False,
            starting_rplfile_id=rplfile.id,
            points=new_activity_data.points,
            compilation_flags=new_activity_data.compilation_flags,
        )
        self.db_session.add(activity)
        self.db_session.commit()
        self.db_session.refresh(activity)
        return activity
    
    def update_activity(
        self,
        activity: Activity,
        new_activity_data: ActivityUpdateRequestDTO
    ) -> Activity:
        if new_activity_data.starting_files:
            compressed_rplfile_bytes = tar_utils.compress_files_to_tar_gz(
                new_activity_data.starting_files
            )
            self.rplfiles_repo.update_rplfile(
                rplfile_id=activity.starting_rplfile_id,
                file_name=datetime.today().strftime("%Y-%m-%d") + ".tar.gz",
                file_type="application/gzip",
                data=compressed_rplfile_bytes,
            )

        for field, new_value in new_activity_data:
            if new_value is not None:
                if field == "language":
                    setattr(activity, field, new_activity_data.language.with_version())
                elif field == "starting_files" or field == "model_config":
                    continue
                else:
                    setattr(activity, field, new_value)

        activity.last_updated = datetime.now(timezone.utc)
        
        self.db_session.commit()
        self.db_session.refresh(activity)
        return activity