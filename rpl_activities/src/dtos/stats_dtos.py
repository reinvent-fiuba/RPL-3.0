from datetime import date
from typing import List, Optional, Union
from pydantic import BaseModel

from rpl_activities.src.repositories.models import aux_models


class SubmissionsStatsOfStudentDTO(BaseModel):
    total_submissions: int
    successful_submissions: int
    submissions_with_runtime_errors: int
    submissions_with_build_errors: int
    submissions_with_failures: int

    name_of_activity_with_the_most_failed_attempts: Optional[str] = None
    amount_of_failed_attempts_for_activity_with_the_most_failed_attempts: Optional[int] = None
    average_failed_attempts_per_activity: Optional[float] = None


class MetadataForActivitiesGroupingDTO(BaseModel):
    id: int
    name: str
    points: int
    category_name: str


class MetadataFoUsersGroupingDTO(BaseModel):
    id: int
    course_user_id: int
    name: str
    surname: str
    username: str
    student_id: str


class MetadataForDateGroupingDTO(BaseModel):
    date: date


# depending on the grouping, the metadata changes
class SubmissionsStatsOfCourseDTO(BaseModel):
    stats_per_student: List[SubmissionsStatsOfStudentDTO]
    grouping_metadata: List[
        Union[MetadataForActivitiesGroupingDTO, MetadataFoUsersGroupingDTO, MetadataForDateGroupingDTO]
    ]
    total_submitters: int
    total_submitters_with_at_least_one_successful_submission: int

    total_submissions_of_all_students: int
    total_successful_submissions_of_all_students: int
    total_errored_submissions_of_all_students: int


class ActivitiesStatsOfStudentDTO(BaseModel):
    amount_of_activities_started: int
    amount_of_activities_not_started: int
    amount_of_activities_solved: int
    points_obtained: int
    total_possible_points: int

    name_of_activity_with_the_most_failed_attempts: Optional[str] = None
    amount_of_failed_attempts_for_activity_with_the_most_failed_attempts: Optional[int] = None
    average_failed_attempts_per_activity: Optional[float] = None
