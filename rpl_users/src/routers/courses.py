from typing import Optional
from fastapi import APIRouter, status
from rpl_users.src.deps.auth import CurrentUserDependency
from rpl_users.src.deps.email import EmailHandlerDependency
from rpl_users.src.deps.database import DBSessionDependency
from rpl_users.src.dtos.role import RoleResponseDTO
from rpl_users.src.dtos.university import UniversityResponseDTO
from rpl_users.src.services.courses import CoursesService


router = APIRouter(prefix="/api/v3", tags=["Courses"])


# ==============================================================================


# ==============================================================================


@router.get("/auth/roles", response_model=list[RoleResponseDTO])
def get_roles(
    db: DBSessionDependency,
):
    return CoursesService(db).get_roles()


@router.get("/auth/universities", response_model=list[UniversityResponseDTO])
def get_universities(
    db: DBSessionDependency,
):
    return CoursesService(db).get_universities()


# ==============================================================================
