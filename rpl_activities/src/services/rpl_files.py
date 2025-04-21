import logging
import os
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse, FileResponse, Response
import mimetypes
import io
import tarfile
import json

from rpl_activities.src.repositories.models.rpl_file import RPLFile
from rpl_activities.src.deps.database import DBSessionDependency
from rpl_activities.src.repositories.rpl_files import RPLFilesRepository


class RPLFilesService:
    def __init__(self, db):
        self.rpl_files_repo = RPLFilesRepository(db)

    def get_file(self, file_id: int) -> Response:

        file = self.rpl_files_repo.get_by_id(file_id)

        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )

        # Get the content type of the file
        mime_type, _ = mimetypes.guess_type(file.file_name)
        if mime_type is None:
            mime_type = "application/gzip"  # Default content type if not determined

        return Response(
            content=file.data,
            media_type=mime_type,
            headers={
                "Content-Disposition": f"attachment; filename={file.file_name}",
                "Content-Type": mime_type,
            },
        )

    def get_extracted_file(self, file_id: int) -> dict[str, str]:
        file = self.rpl_files_repo.get_by_id(file_id)

        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )

        # Check if the file is a tar.xz file
        if not file.file_name.endswith(".tar.xz"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is not a tar.xz file",
            )

        return self.__extract_tar_gz_to_dict(file.data)

    def get_extracted_files(self, file_ids: list[int]) -> list[dict[str, str]]:
        files: list[dict[str, str]] = []
        for file_id in file_ids:
            file = self.get_extracted_file(file_id)
            files.append(file)
        return files

    def extract_file_for_student(self, file_id: int) -> dict[str, str]:
        extracted_files = self.get_extracted_file(file_id)
        if not extracted_files:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No files extracted",
            )

        if "files_metadata" not in extracted_files:
            return extracted_files

        metadata_file_data = extracted_files["files_metadata"]

        try:
            if isinstance(metadata_file_data, list):
                # If metadata is a list, take the first element
                metadata_dict = json.loads(metadata_file_data[0])
            else:
                metadata_dict = json.loads(extracted_files["files_metadata"])
        except json.JSONDecodeError:
            logging.warning(
                f"File metadata bad formated {file_id}: {extracted_files['files_metadata']}"
            )
            return extracted_files

        filtered_files: dict[str, str] = {}

        # Extracts the tar.gz and returns the files as a Map where the key is the filename and the
        # value is the file content. Only returns files with metadata {"display": "read"} or
        # {"display": "read_write"}. Doesn't return files with metadata {display: "hidden"}

        for filename, file_content in extracted_files.items():
            if filename == "files_metadata":
                continue
            if filename not in metadata_dict:
                filtered_files[filename] = file_content
            try:
                metadata = metadata_dict[filename]
                if not metadata["display"] == "hidden":
                    filtered_files[filename] = file_content
            except json.JSONDecodeError:
                logging.warning(
                    f"File metadata bad formated {filename}: {file_content}"
                )
                continue
        return filtered_files

    def get_extracted_files_for_student(
        self, file_ids: list[int]
    ) -> list[dict[str, str]]:
        files: list[dict[str, str]] = []
        for file_id in file_ids:
            file = self.extract_file_for_student(file_id)
            files.append(file)
        return files

    # =========================
    # Private methods
    # =========================

    def __extract_tar_gz_to_dict(self, data: bytes) -> dict[str, str]:
        extracted_files = {}

        with tarfile.open(fileobj=io.BytesIO(data), mode="r") as tar:
            for member in tar.getmembers():
                if member.isfile():
                    file = tar.extractfile(member)
                    if file:
                        try:
                            decoded_chunks = []
                            while True:
                                chunk = file.read(8192)
                                if not chunk:
                                    break
                                decoded_chunks.append(chunk.decode("utf-8"))
                            extracted_files[os.path.basename(member.name)] = (
                                decoded_chunks
                            )
                        except UnicodeDecodeError:
                            logging.warning(f"Could not decode {member.name} as UTF-8.")
        return extracted_files
