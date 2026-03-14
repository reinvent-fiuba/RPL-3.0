from typing import List, Optional

import sqlalchemy as sa

from rpl_activities.src.repositories.base import BaseRepository

from .models.rpl_file import RPLFile


class RPLFilesRepository(BaseRepository):
    def get_by_id(self, file_id: int) -> Optional[RPLFile]:
        return (
            self.db_session.execute(sa.select(RPLFile).where(RPLFile.id == file_id)).scalars().one_or_none()
        )

    def create_rplfile(self, file_name: str, file_type: str, data: bytes) -> RPLFile:
        rplfile = RPLFile(file_name=file_name, file_type=file_type, data=data)
        self.db_session.add(rplfile)
        self.db_session.commit()
        self.db_session.refresh(rplfile)
        return rplfile

    def clone_rplfile(self, rplfile: RPLFile) -> RPLFile:
        new_rplfile = RPLFile(file_name=rplfile.file_name, file_type=rplfile.file_type, data=rplfile.data)
        self.db_session.add(new_rplfile)
        self.db_session.commit()
        self.db_session.refresh(new_rplfile)
        return new_rplfile

    def update_rplfile(self, rplfile_id: int, file_name: str, file_type: str, data: bytes) -> RPLFile:
        rplfile = self.get_by_id(rplfile_id)
        rplfile.file_name = file_name
        rplfile.file_type = file_type
        rplfile.data = data
        self.db_session.commit()
        self.db_session.refresh(rplfile)
        return rplfile

    def delete_rplfiles(self, rplfiles_ids: List[int]) -> None:
        if not rplfiles_ids:
            return
        self.db_session.execute(sa.delete(RPLFile).where(RPLFile.id.in_(rplfiles_ids)))
        self.db_session.commit()
