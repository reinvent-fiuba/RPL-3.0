from typing import Optional
from fastapi import APIRouter, status

from rpl_activities.src.deps.database import DBSessionDependency
from rpl_activities.src.services.rpl_files import RPLFilesService


router = APIRouter(prefix="/api/v3", tags=["RPLFiles"])


@router.get("/files/{file_id}", status_code=status.HTTP_200_OK)
async def get_file(
    file_id: int,
    db: DBSessionDependency,
):
    return RPLFilesService(db).get_file(file_id)


@router.get("/getExtractedFile/{file_id}", status_code=status.HTTP_200_OK)
async def get_extracted_file(
    file_id: int,
    db: DBSessionDependency,
):
    return RPLFilesService(db).get_extracted_file(file_id)


@router.get("/getExtractedFileForStudent/{file_id}", status_code=status.HTTP_200_OK)
async def get_extracted_file_for_student(
    file_id: int,
    db: DBSessionDependency,
):
    return RPLFilesService(db).extract_file_for_student(file_id)


@router.get("/getExtractedFiles", status_code=status.HTTP_200_OK)
async def get_extracted_files(
    file_ids: list[int],
    db: DBSessionDependency,
):
    if file_ids is None:
        return []
    return RPLFilesService(db).get_extracted_files(file_ids)


@router.get("/getExtractedFilesForStudent", status_code=status.HTTP_200_OK)
async def get_extracted_files_for_student(
    file_ids: list[int],
    db: DBSessionDependency,
):
    if file_ids is None:
        return []
    return RPLFilesService(db).extract_files_for_student(file_ids)
