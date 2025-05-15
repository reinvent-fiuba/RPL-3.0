import logging
from fastapi import HTTPException, status
from rpl_activities.src.deps.auth import CurrentCourseUser
from rpl_activities.src.dtos.activity_dtos import (
    IOTestDTO,
    CreateUnitTestRequestDTO,
    AllActivitiesResponseDTO,
    ActivityCreationRequestDTO,
    ActivityUpdateRequestDTO,
    ActivityResponseDTO
)
from rpl_activities.src.repositories.activities import ActivitiesRepository
from rpl_activities.src.repositories.models.activity import Activity

class ActivitiesService:
    pass