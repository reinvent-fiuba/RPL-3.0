from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse, FileResponse, Response
import mimetypes
from tempfile import NamedTemporaryFile

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
