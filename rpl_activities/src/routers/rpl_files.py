from typing import Optional
from fastapi import APIRouter, status

from rpl_activities.src.deps.database import DBSessionDependency
from rpl_activities.src.services.rpl_files import RPLFilesService


router = APIRouter(prefix="/api/v3", tags=["RPLFiles"])


@router.get("/files/{file_id}", status_code=status.HTTP_200_OK)
async def get_file(
    file_id: int,
    db: DBSessionDependency,
) -> Optional[bytes]:
    """
    Get a file as is by its ID.
    """
    # response headers
    headers = {
        "Content-Disposition": f"attachment; filename={file_id}",
        "Content-Type": "application/octet-stream",
    }
    # return file bytes with headers
    file = RPLFilesService(db).get_file(file_id)
    if not file:
        return None
    return {
        "headers": headers,
        "content": file,
    }
