from datetime import datetime
from typing import List, Optional
from fastapi import File, UploadFile
from pydantic import BaseModel

from rpl_activities.src.repositories.models import aux_models


class IOTestRequestDTO(BaseModel):
    name: str
    test_in: str
    test_out: str

class IOTestResponseDTO(BaseModel):
    id: int
    name: str
    test_in: str
    test_out: str

class CreateUnitTestRequestDTO(BaseModel):
    unit_test_code: str


# ==============================================================================


class ActivityWithMetadataOnlyResponseDTO(BaseModel):
    course_id: int
    category_id: int
    category_name: str
    category_description: str
    name: str
    description: str = ""
    language: aux_models.Language
    is_io_tested: bool
    active: bool
    deleted: bool
    points: int
    starting_rplfile_id: int
    submission_status: aux_models.SubmissionStatus
    last_submission_date: Optional[datetime] = None
    date_created: datetime
    last_updated: datetime



class ActivityCreationRequestDTO(BaseModel):
    category_id: int
    name: str
    description: Optional[str] = None
    language: aux_models.Language
    compilation_flags: Optional[str] = None
    active: bool = True
    points: int
    startingFile: List[UploadFile] = File(...)
    model_config = {"extra": "forbid"}


class ActivityUpdateRequestDTO(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    language: Optional[aux_models.Language] = None
    compilation_flags: Optional[str] = None
    active: Optional[bool] = None
    points: Optional[int] = None
    startingFile: Optional[List[UploadFile]] = File(None)
    model_config = {"extra": "forbid"}


class ActivityResponseDTO(BaseModel):
    course_id: int
    category_id: int
    category_name: str
    category_description: str
    name: str
    description: str = ""
    language: aux_models.Language
    is_io_tested: bool
    active: bool
    deleted: bool
    points: int
    starting_rplfile_id: int
    activity_unittests: str = ""
    compilation_flags: str = ""
    activity_iotests: List[IOTestResponseDTO] = []
    date_created: datetime
    last_updated: datetime


# ==============================================================================

