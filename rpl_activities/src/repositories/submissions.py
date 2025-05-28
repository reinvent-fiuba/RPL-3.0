from datetime import datetime, timezone
import json
from fastapi import UploadFile

from rpl_activities.src.deps.auth import CurrentCourseUser
from rpl_activities.src.dtos.submission_dtos import SubmissionCreationRequestDTO, UpdateSubmissionStatusRequestDTO
from rpl_activities.src.repositories.base import BaseRepository
import sqlalchemy as sa

from rpl_activities.src.repositories.models import aux_models
from rpl_activities.src.repositories.models.activity import Activity
from rpl_activities.src.repositories.rpl_files import RPLFilesRepository
from rpl_activities.src.deps import tar_utils
from .models.activity_submission import ActivitySubmission

class SubmissionsRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db)
        self.rplfiles_repo = RPLFilesRepository(db)

    # =================================================================


    def get_best_submission_status_by_user_at_activity(
        self, user_id: int , activity: Activity, current_user_submissions_at_activity: list[ActivitySubmission]
    ) -> aux_models.SubmissionStatus:
        if len(current_user_submissions_at_activity) == 0:
            return aux_models.SubmissionStatus.NO_SUBMISSIONS

        statuses = [submission.status for submission in current_user_submissions_at_activity]

        status_order = list(aux_models.SubmissionStatus)
        best_status = max(
            statuses,
            key=lambda status: status_order.index(status)
        )
        return best_status
 

    def get_last_submission_date_by_user_at_activity(
        self, user_id: int , activity: Activity, current_user_submissions_at_activity: list[ActivitySubmission]
    ) -> datetime:
        if len(current_user_submissions_at_activity) == 0:
            return None
        last_submission = max(
            current_user_submissions_at_activity,
            key=lambda submission: submission.date_created
        )
        return last_submission.date_created
    

    def get_all_submissions_by_current_user_at_activities(
        self, user_id: int , activities: list[Activity]
    ):
        if len(activities) == 0:
            return []
        return (
            self.db_session.execute(
                sa.select(ActivitySubmission).where(
                    ActivitySubmission.user_id == user_id,
                    ActivitySubmission.activity_id.in_([activity.id for activity in activities]),
                )
            )
            .scalars()
            .all()
        )
    
    # =================================================================

    def get_by_id(
        self, submission_id: int
    ) -> ActivitySubmission | None:
        return (
            self.db_session.execute(
                sa.select(ActivitySubmission).where(
                    ActivitySubmission.id == submission_id
                )
            )
            .scalars()
            .one_or_none()
        )
    
    
    def __get_verified_submission_files_to_compress(
        self,
        extracted_starting_files: tar_utils.ExtractedFilesDict,
        submission_uploadfiles: list[UploadFile]
    ) -> dict[str, bytes]:
        starting_files_metadata = extracted_starting_files.get("files_metadata")
        if not starting_files_metadata:
            return tar_utils.compress_uploadfiles_to_tar_gz(submission_uploadfiles)
        starting_files_metadata: dict[str, str] = json.loads(starting_files_metadata)
        files_to_compress = {}
        for uploadfile in submission_uploadfiles:
            if uploadfile.filename in starting_files_metadata.keys():
                if starting_files_metadata[uploadfile.filename]["display"] == "read_write":
                    files_to_compress[uploadfile.filename] = uploadfile.file.read()
                else:
                    files_to_compress[uploadfile.filename] = extracted_starting_files[uploadfile.filename].encode()
            else:
                files_to_compress[uploadfile.filename] = uploadfile.file.read()

        for starting_file_name, starting_file_content in extracted_starting_files.items():
            if starting_file_name not in files_to_compress.keys():
                files_to_compress[starting_file_name] = starting_file_content.encode()

        return files_to_compress

 
    def create_submission_for_activity(
        self,
        new_submission_data: SubmissionCreationRequestDTO,
        activity: Activity,
        current_course_user: CurrentCourseUser,
    ) -> ActivitySubmission:
        extracted_starting_files = tar_utils.extract_tar_gz_to_dict_of_files(activity.starting_rplfile.data)
        verified_raw_submission_files = self.__get_verified_submission_files_to_compress(
            extracted_starting_files,
            new_submission_data.file
        )
        compressed_submission_files = tar_utils.compress_files_dict_to_tar_gz(verified_raw_submission_files)
        rplfile = self.rplfiles_repo.create_rplfile(
            file_name=f"{datetime.today().strftime('%Y-%m-%d')}__{current_course_user.course_id}__{activity.id}__{current_course_user.user_id}_SUBM.tar.gz",
            file_type=aux_models.RPLFileType.GZIP,
            data=compressed_submission_files
        )
        submission = ActivitySubmission(
            is_final_solution=False,
            activity_id=activity.id,
            user_id=current_course_user.user_id,
            response_rplfile_id=rplfile.id,
            status=aux_models.SubmissionStatus.PENDING,
            date_created=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc)
        )
        self.db_session.add(submission)
        self.db_session.commit()
        self.db_session.refresh(submission)
        return submission

    def update_submission_status(
        self,
        submission: ActivitySubmission,
        new_status_data: UpdateSubmissionStatusRequestDTO
    ) -> ActivitySubmission:
        submission.status = new_status_data.status
        submission.last_updated = datetime.now(timezone.utc)
        self.db_session.commit()
        self.db_session.refresh(submission)
        return submission

    def mark_submission_as_final_solution(
        self,
        submission: ActivitySubmission
    ) -> ActivitySubmission:
        submission.is_final_solution = True
        submission.last_updated = datetime.now(timezone.utc)
        self.db_session.commit()
        self.db_session.refresh(submission)
        return submission
    
    def get_final_submission_by_current_user_from_activity(
        self,
        activity_id: int,
        current_course_user: CurrentCourseUser
    ) -> ActivitySubmission | None:
        return (
            self.db_session.execute(
                sa.select(ActivitySubmission).where(
                    ActivitySubmission.activity_id == activity_id,
                    ActivitySubmission.user_id == current_course_user.user_id,
                    ActivitySubmission.is_final_solution == True,
                )
            )
            .scalars()
            .one_or_none()
        )