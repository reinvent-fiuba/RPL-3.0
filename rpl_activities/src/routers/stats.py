from typing import Optional
from fastapi import APIRouter, Query, status
from datetime import date

from rpl_activities.src.deps.auth import AllStudentsCourseUsersDependency, CurrentCourseUserDependency
from rpl_activities.src.deps.database import DBSessionDependency
from rpl_activities.src.services.stats import StatsService
from rpl_activities.src.dtos.stats_dtos import (
    SubmissionsStatsOfCourseDTO,
    ActivitiesStatsOfStudentDTO,
    SubmissionsStatsOfStudentDTO,
)

router = APIRouter(prefix="/api/v3", tags=["Stats"])

# ==============================================================================


@router.get("/stats/courses/{courseId}/activities/me", response_model=ActivitiesStatsOfStudentDTO)
def get_activities_stats_for_current_user(
    course_id: int, current_course_user: CurrentCourseUserDependency, db: DBSessionDependency
):
    return StatsService(db).get_activities_stats_for_current_user(course_id, current_course_user)


@router.get("/stats/courses/{courseId}/submissions/me", response_model=SubmissionsStatsOfStudentDTO)
def get_submissions_stats_for_current_user(
    course_id: int, current_course_user: CurrentCourseUserDependency, db: DBSessionDependency
):
    return StatsService(db).get_submissions_stats_for_current_user(course_id, current_course_user)


@router.get("/stats/courses/{courseId}/submissions", response_model=SubmissionsStatsOfCourseDTO)
def get_submissions_stats_for_all_students_or_specific_user(
    course_id: int,
    current_course_user: CurrentCourseUserDependency,
    all_students_course_users: AllStudentsCourseUsersDependency,
    db: DBSessionDependency,
    date: Optional[date] = None,
    category_id: Optional[int] = None,
    user_id: Optional[int] = None,
    activity_id: Optional[int] = None,
    group_by: Optional[str] = Query(None, pattern="^(date|user|activity)?$"),
):
    return StatsService(db).get_submissions_stats_for_students_according_to_filters(
        current_course_user,
        all_students_course_users,
        course_id,
        date,
        category_id,
        user_id,
        activity_id,
        group_by,
    )
