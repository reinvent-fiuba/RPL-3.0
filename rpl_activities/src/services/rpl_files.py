import logging
from fastapi import HTTPException, status
from fastapi.responses import Response
import json

from rpl_activities.src.deps.tar_utils import ExtractedFilesDict
from rpl_activities.src.deps import tar_utils
from rpl_activities.src.repositories.models import aux_models
from rpl_activities.src.repositories.models.rpl_file import RPLFile
from rpl_activities.src.repositories.rpl_files import RPLFilesRepository


class RPLFilesService:
    def __init__(self, db):
        self.rpl_files_repo = RPLFilesRepository(db)

    def get_raw_rplfile(self, rplfile_id: int) -> Response:
        file = self.rpl_files_repo.get_by_id(rplfile_id)
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )
        return Response(
            content=file.data,
            media_type=file.file_type,
            headers={
                "Content-Disposition": f"attachment; filename={file.file_name}",
                "Content-Type": file.file_type,
            },
        )

    def get_extracted_rplfile(self, rplfile_id: int) -> ExtractedFilesDict:
        rplfile = self.rpl_files_repo.get_by_id(rplfile_id)
        if not rplfile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )
        if rplfile.file_type != aux_models.RPLFileType.GZIP:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is not a gzip file",
            )
        return tar_utils.extract_tar_gz_to_dict_of_files(rplfile.data)

    def get_multiple_extracted_rplfiles(self, raw_rplfiles_ids: str) -> list[ExtractedFilesDict]:
        rplfiles_ids: list[int] = [int(rplfile_id) for rplfile_id in raw_rplfiles_ids.split(",")]
        extracted_rplfiles: list[ExtractedFilesDict] = []
        for rplfile_id in rplfiles_ids:
            files = self.get_extracted_rplfile(rplfile_id)
            extracted_rplfiles.append(files)
        return extracted_rplfiles

    def get_extracted_rplfile_for_student(self, rplfile_id: int) -> ExtractedFilesDict:
        extracted_rplfile: ExtractedFilesDict = self.get_extracted_rplfile(rplfile_id)
        if not extracted_rplfile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No files extracted",
            )

        if tar_utils.METADATA_FILENAME not in extracted_rplfile:
            return extracted_rplfile
        raw_metadata_file = extracted_rplfile[tar_utils.METADATA_FILENAME]
        try:
            general_metadata_dict = json.loads(raw_metadata_file)
        except json.JSONDecodeError:
            logging.warning(f"Metadata file: JSON decode error for {rplfile_id}: {raw_metadata_file}")
            return {}

        filtered_files: ExtractedFilesDict = {}
        for filename, file_content in extracted_rplfile.items():
            if filename == tar_utils.METADATA_FILENAME:
                continue
            if filename not in general_metadata_dict:
                filtered_files[filename] = file_content
            else:
                metadata_for_current_file = general_metadata_dict[filename]
                if "display" in metadata_for_current_file:
                    if metadata_for_current_file["display"] != "hidden":
                        filtered_files[filename] = file_content
        return filtered_files

    def get_multiple_extracted_rplfiles_for_student(self, raw_rplfiles_ids: str) -> list[ExtractedFilesDict]:
        rplfiles_ids: list[int] = [int(rplfile_id) for rplfile_id in raw_rplfiles_ids.split(",")]
        extracted_rplfiles: list[ExtractedFilesDict] = []
        for rplfile_id in rplfiles_ids:
            extracted_rplfile = self.get_extracted_rplfile_for_student(rplfile_id)
            extracted_rplfiles.append(extracted_rplfile)
        return extracted_rplfiles
