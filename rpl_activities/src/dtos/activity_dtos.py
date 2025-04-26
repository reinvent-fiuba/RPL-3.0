from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from rpl_activities.src.repositories.models import aux_models


class AllActivitiesResponseDTO(BaseModel):
    name: str
    description: Optional[str] = None
    language: aux_models.Language
    is_io_tested: bool
    points: int
    submission_status: aux_models.SubmissionStatus
    last_submission_date: Optional[datetime]
    date_created: datetime
    last_updated: datetime


class ActivityResponseDTO(BaseModel):
    id: int
    course_id: int
    category_id: int
    name: str
    description: Optional[str] = None
    language: aux_models.Language
    is_io_tested: bool
    active: bool
    deleted: bool
    points: int
    starting_rplfile_id: Optional[int] = None
