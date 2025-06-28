from datetime import date
from typing import List, Optional, Union
from pydantic import BaseModel

from rpl_activities.src.repositories.models import aux_models


class SubmissionsStatsDTO(BaseModel):
    total_submissions: int
    successful_submissions: int
    submissions_with_runtime_errors: int
    submissions_with_build_errors: int
    submissions_with_failures: int
    avg_submissions_by_student: Optional[float]
    avg_error_submissions_by_student: Optional[float]
    avg_success_submissions_by_student: Optional[float]
    total_submitters: Optional[int]
    total_submitters_with_at_least_one_successful_submission: Optional[int]
    total_submitters_without_successful_submissions: Optional[int]


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
class GroupedSubmissionsStatsDTO(BaseModel):
    submissions_stats: List[SubmissionsStatsDTO]
    metadata: List[
        Union[MetadataForActivitiesGroupingDTO, MetadataFoUsersGroupingDTO, MetadataForDateGroupingDTO]
    ]


class ActivitiesStatsOfStudentDTO(BaseModel):
    amount_of_activities_started: int
    amount_of_activities_not_started: int
    amount_of_activities_solved: int
    points_obtained: int
    total_possible_points: int


class BasicActivitiesStatsOfStudentDTO(BaseModel):
    user_id: int
    total_score: int
    successful_activities_count: int
