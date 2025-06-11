from typing import Optional
from fastapi import APIRouter, status

from rpl_activities.src.deps.auth import CurrentCourseUserDependency, RunnerAuthDependency
from rpl_activities.src.deps.database import DBSessionDependency
from rpl_activities.src.services.rpl_files import RPLFilesService


router = APIRouter(prefix="/api/v3", tags=["RPLFiles"])


@router.get("/RPLFile/{rplfile_id}")
def get_raw_rplfile(rplfile_id: int, runner_auth: RunnerAuthDependency, db: DBSessionDependency):
    return RPLFilesService(db).get_raw_rplfile_for_runner(rplfile_id)


@router.get("/courses/{course_id}/extractedRPLFile/{rplfile_id}")
def get_extracted_rplfile(
    course_id: int, rplfile_id: int, current_course_user: CurrentCourseUserDependency, db: DBSessionDependency
):
    return RPLFilesService(db).get_extracted_rplfile_for_teacher(rplfile_id, current_course_user)


@router.get("/courses/{course_id}/extractedRPLFileForStudent/{rplfile_id}")
def get_extracted_rplfile_for_student(
    course_id: int, rplfile_id: int, current_course_user: CurrentCourseUserDependency, db: DBSessionDependency
):
    return RPLFilesService(db).get_extracted_rplfile_for_student(rplfile_id, current_course_user)


@router.get("/courses/{course_id}/extractedRPLFilesForStudent/{rplfiles_ids}")
def get_multiple_extracted_rplfiles_for_student(
    course_id: int,
    rplfiles_ids: str,
    current_course_user: CurrentCourseUserDependency,
    db: DBSessionDependency,
):
    return RPLFilesService(db).get_multiple_extracted_rplfiles_for_student(rplfiles_ids, current_course_user)
