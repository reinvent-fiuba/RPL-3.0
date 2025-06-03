from datetime import datetime, timezone

from rpl_activities.src.deps import tar_utils
from rpl_activities.src.dtos.activity_dtos import (
    ActivityCreationRequestDTO,
    ActivityUpdateRequestDTO,
    IOTestResponseDTO,
)
from rpl_activities.src.repositories.base import BaseRepository
import sqlalchemy as sa

from rpl_activities.src.repositories.models import aux_models
from rpl_activities.src.repositories.models.activity_category import ActivityCategory
from rpl_activities.src.repositories.rpl_files import RPLFilesRepository
from .models.activity import Activity

MAX_ACTIVITY_NAME_LEN_FOR_TAR = 180


class ActivitiesRepository(BaseRepository):
    def __init__(self, db_session):
        super().__init__(db_session)
        self.rplfiles_repo = RPLFilesRepository(db_session)

    # ====================== QUERYING ====================== #

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

    def get_all_activities_by_category_id(self, category_id: int) -> list[Activity]:
        return (
            self.db_session.execute(
                sa.select(Activity).where(
                    Activity.category_id == category_id,
                    Activity.deleted == False,
                )
            )
            .scalars()
            .all()
        )

    def get_unit_tests_data_from_activity(self, activity: Activity) -> str:
        return activity.unit_test_suite.test_rplfile.data.decode() if activity.unit_test_suite else ""

    def get_io_tests_data_from_activity(self, activity: Activity) -> list[IOTestResponseDTO]:
        io_tests = activity.io_tests
        return (
            [
                IOTestResponseDTO(
                    id=io_test.id,
                    name=io_test.name,
                    test_in=io_test.test_in,
                    test_out=io_test.test_out,
                )
                for io_test in io_tests
            ]
            if io_tests
            else []
        )

    # ====================== MANAGING ====================== #

    def delete_activity(self, activity: Activity):
        activity.deleted = True
        activity.last_updated = datetime.now(timezone.utc)
        self.db_session.commit()

    def create_activity(self, course_id: int, new_activity_data: ActivityCreationRequestDTO) -> Activity:
        compressed_rplfile_bytes = tar_utils.compress_uploadfiles_to_tar_gz(new_activity_data.starting_files)
        truncated_act_name = new_activity_data.name.strip()[:MAX_ACTIVITY_NAME_LEN_FOR_TAR]
        rplfile = self.rplfiles_repo.create_rplfile(
            file_name=f"{datetime.today().strftime('%Y-%m-%d')}__{course_id}__ACT__{truncated_act_name}.tar.gz",
            file_type=aux_models.RPLFileType.GZIP,
            data=compressed_rplfile_bytes,
        )

        if (new_activity_data.compilation_flags is None) and (
            new_activity_data.language == aux_models.Language.C
        ):
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

    def clone_activity(self, activity: Activity, to_category: ActivityCategory) -> Activity:
        starting_rplfile = self.rplfiles_repo.get_by_id(activity.starting_rplfile_id)
        new_starting_rplfile = self.rplfiles_repo.clone_rplfile(starting_rplfile)
        new_activity = Activity(
            course_id=to_category.course_id,
            category_id=to_category.id,
            name=activity.name,
            description=activity.description,
            language=activity.language,
            is_io_tested=activity.is_io_tested,
            active=activity.active,
            deleted=False,
            starting_rplfile_id=new_starting_rplfile.id,
            points=activity.points,
            compilation_flags=activity.compilation_flags,
        )
        self.db_session.add(new_activity)
        self.db_session.commit()
        self.db_session.refresh(new_activity)
        return new_activity

    def update_activity(
        self,
        course_id: int,
        activity: Activity,
        new_activity_data: ActivityUpdateRequestDTO,
    ) -> Activity:
        if new_activity_data.starting_files:
            compressed_rplfile_bytes = tar_utils.compress_uploadfiles_to_tar_gz(
                new_activity_data.starting_files
            )
            if new_activity_data.name:
                truncated_act_name = new_activity_data.name.strip()[:MAX_ACTIVITY_NAME_LEN_FOR_TAR]
            else:
                truncated_act_name = activity.name.strip()[:MAX_ACTIVITY_NAME_LEN_FOR_TAR]
            self.rplfiles_repo.update_rplfile(
                rplfile_id=activity.starting_rplfile_id,
                file_name=f"{datetime.today().strftime('%Y-%m-%d')}__{course_id}__ACT__{truncated_act_name}.tar.gz",
                file_type=aux_models.RPLFileType.GZIP,
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

    def update_iotest_mode_for_activity(self, activity: Activity, is_io_tested: bool) -> Activity:
        activity.is_io_tested = is_io_tested
        activity.last_updated = datetime.now(timezone.utc)
        self.db_session.commit()
        self.db_session.refresh(activity)
        return activity

    def enable_iotest_mode_for_activity(self, activity: Activity) -> Activity:
        if not activity.is_io_tested:
            activity = self.update_iotest_mode_for_activity(activity, True)
        return activity

    def disable_iotest_mode_for_activity(self, activity: Activity) -> Activity:
        if activity.is_io_tested:
            activity = self.update_iotest_mode_for_activity(activity, False)
        return activity
