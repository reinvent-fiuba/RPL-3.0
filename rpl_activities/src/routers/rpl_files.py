from typing import Optional
from fastapi import APIRouter, status

from rpl_activities.src.deps.database import DBSessionDependency
from rpl_activities.src.services.rpl_files import RPLFilesService


router = APIRouter(prefix="/api/v3", tags=["RPLFiles"])


@router.get("/RPLFile/{rplfile_id}")
def get_raw_rplfile(rplfile_id: int, db: DBSessionDependency):
    return RPLFilesService(db).get_raw_rplfile(rplfile_id)


@router.get("/extractedRPLFile/{rplfile_id}")
def get_extracted_rplfile(rplfile_id: int, db: DBSessionDependency):
    return RPLFilesService(db).get_extracted_rplfile(rplfile_id)


@router.get("/extractedRPLFiles/{rplfiles_ids}")
def get_multiple_extracted_rplfiles(rplfiles_ids: str, db: DBSessionDependency):
    return RPLFilesService(db).get_multiple_extracted_rplfiles(rplfiles_ids)


@router.get("/extractedRPLFileForStudent/{rplfile_id}")
def get_extracted_rplfile_for_student(rplfile_id: int, db: DBSessionDependency):
    return RPLFilesService(db).get_extracted_rplfile_for_student(rplfile_id)


@router.get("/extractedRPLFilesForStudent/{rplfiles_ids}")
def get_multiple_extracted_rplfiles_for_student(rplfiles_ids: str, db: DBSessionDependency):
    return RPLFilesService(db).get_multiple_extracted_rplfiles_for_student(rplfiles_ids)
