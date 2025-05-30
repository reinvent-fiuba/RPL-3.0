import logging
from fastapi import HTTPException, status
from rpl_activities.src.deps.auth import CurrentCourseUser
from rpl_activities.src.dtos.activity_dtos import (
    ActivityWithMetadataOnlyResponseDTO,
    ActivityCreationRequestDTO,
    ActivityUpdateRequestDTO,
    ActivityResponseDTO
)
from rpl_activities.src.repositories.activities import ActivitiesRepository
from rpl_activities.src.repositories.categories import CategoriesRepository
from rpl_activities.src.repositories.models import aux_models
from rpl_activities.src.repositories.models.activity import Activity
from rpl_activities.src.repositories.models.activity_submission import ActivitySubmission
from rpl_activities.src.repositories.submissions import SubmissionsRepository

class ActivitiesService:
    def __init__(self, db):
        self.activities_repo = ActivitiesRepository(db)
        self.submissions_repo = SubmissionsRepository(db)
        self.categories_repo = CategoriesRepository(db)


    def verify_permission_to_view(self, current_course_user: CurrentCourseUser):
        can_view_activities = current_course_user.has_authority("activity_view")
        if not can_view_activities:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view activities on this course",
            )
        
    def verify_permission_to_manage(self, current_course_user: CurrentCourseUser):
        can_manage_activities = current_course_user.has_authority("activity_manage")
        if not can_manage_activities:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to manage activities on this course",
            )

    def has_permission_to_manage(self, current_course_user: CurrentCourseUser):
        return current_course_user.has_authority("activity_manage")

    def verify_permission_to_submit(self, current_course_user: CurrentCourseUser):
        can_submit_solutions = current_course_user.has_authority("activity_submit")
        if not can_submit_solutions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to submit activities on this course",
            )
        
    def verify_and_get_activity(
        self,
        course_id: int,
        activity_id: int,
    ) -> Activity:
        activity = self.activities_repo.get_activity_by_id(activity_id)
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found",
            )
        if activity.course_id != course_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Activity does not belong to the course",
            )
        return activity

    
    # ==============================================================================

    def __get_all_activities_for_user_depending_on_permission(
            self, 
            current_course_user: CurrentCourseUser, 
            course_id: int
    ) -> list[Activity]:
        if self.has_permission_to_manage(current_course_user):
            activities = self.activities_repo.get_all_activities_by_course_id(course_id)
        else:
            activities = self.activities_repo.get_all_active_activities_by_course_id(course_id)
        return activities


    def __group_submissions_by_activity(self, submissions: list[ActivitySubmission]) -> dict[int, list[ActivitySubmission]]:
        submissions_by_activity: dict[int, list[ActivitySubmission]] = {}
        for submission in submissions:
            activity_id = submission.activity_id
            if activity_id not in submissions_by_activity:
                submissions_by_activity[activity_id] = []
            submissions_by_activity[activity_id].append(submission)
        return submissions_by_activity


    def build_activity_metadata_response_dto(
            self,
            activity: Activity,
            course_id: int,
            current_course_user: CurrentCourseUser,
            current_user_submissions_at_activity: list[ActivitySubmission]
    ) -> ActivityWithMetadataOnlyResponseDTO:
        return ActivityWithMetadataOnlyResponseDTO(
            course_id=course_id,
            category_id=activity.category_id,
            category_name=activity.category.name,
            category_description=activity.category.description,
            name=activity.name,
            description=activity.description,
            language=aux_models.LanguageWithVersion(activity.language).without_version(),
            is_io_tested=activity.is_io_tested,
            active=activity.active,
            deleted=activity.deleted,
            points=activity.points,
            starting_rplfile_id=activity.starting_rplfile.id,
            submission_status=self.submissions_repo.get_best_submission_status_by_user_at_activity(
                current_course_user.user_id, activity, current_user_submissions_at_activity
            ),
            last_submission_date=self.submissions_repo.get_last_submission_date_by_user_at_activity(
                current_course_user.user_id, activity, current_user_submissions_at_activity
            ),
            date_created=activity.date_created,
            last_updated=activity.last_updated
        )


    def build_activity_response_dto(self, activity: Activity) -> ActivityResponseDTO:
        unit_tests_data = self.activities_repo.get_unit_tests_data_from_activity(activity)
        io_tests_data = self.activities_repo.get_io_tests_data_from_activity(activity)
        return ActivityResponseDTO(
            course_id=activity.course_id,
            category_id=activity.category_id,
            category_name=activity.category.name,
            category_description=activity.category.description,
            name=activity.name,
            description=activity.description,
            language=aux_models.LanguageWithVersion(activity.language).without_version(),
            is_io_tested=activity.is_io_tested,
            active=activity.active,
            deleted=activity.deleted,
            points=activity.points,
            starting_rplfile_id=activity.starting_rplfile.id,
            activity_unittests=unit_tests_data,
            activity_iotests=io_tests_data,
            compilation_flags=activity.compilation_flags,
            date_created=activity.date_created,
            last_updated=activity.last_updated
        )


    # ==============================================================================


    def get_all_activities_for_current_user(
            self, 
            current_course_user: CurrentCourseUser, 
            course_id: int
    ) -> list[ActivityWithMetadataOnlyResponseDTO]:
        self.verify_permission_to_view(current_course_user)
        activities = self.__get_all_activities_for_user_depending_on_permission(
            current_course_user, course_id
        )
        if not activities:
            return []

        all_submissions_by_current_user = self.submissions_repo.get_all_submissions_by_current_user_at_activities(
            current_course_user.user_id, activities
        )
        current_user_submissions_by_activity = self.__group_submissions_by_activity(all_submissions_by_current_user)
        return [
            self.build_activity_metadata_response_dto(
                activity, course_id, current_course_user, current_user_submissions_by_activity.get(activity.id, [])
            )
            for activity in activities
        ]

    
    def get_activity(
            self, 
            current_course_user: CurrentCourseUser,
            course_id: int,
            activity_id: int
    ) -> ActivityResponseDTO:
        self.verify_permission_to_view(current_course_user)
        activity = self.verify_and_get_activity(course_id, activity_id)
        return self.build_activity_response_dto(activity)


    def delete_activity(
            self, 
            current_course_user: CurrentCourseUser,
            course_id: int,
            activity_id: int
    ) -> ActivityResponseDTO:
        self.verify_permission_to_manage(current_course_user)
        activity = self.verify_and_get_activity(course_id, activity_id)
        self.activities_repo.delete_activity(activity)
        return self.build_activity_response_dto(activity)


    def create_activity(
            self, 
            current_course_user: CurrentCourseUser,
            course_id: int,
            new_activity_data: ActivityCreationRequestDTO
    ) -> ActivityResponseDTO:
        self.verify_permission_to_manage(current_course_user)
        category = self.categories_repo.get_category_by_id_and_course_id(
            new_activity_data.category_id, course_id
        )
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
        activity = self.activities_repo.create_activity(
            course_id, new_activity_data
        )
        return self.build_activity_response_dto(activity)


    def update_activity(
            self, 
            current_course_user: CurrentCourseUser,
            course_id: int,
            activity_id: int,
            new_activity_data: ActivityUpdateRequestDTO
    ) -> ActivityResponseDTO:
        self.verify_permission_to_manage(current_course_user)
        activity = self.verify_and_get_activity(course_id, activity_id)
        updated_activity = self.activities_repo.update_activity(course_id, activity, new_activity_data)
        return self.build_activity_response_dto(updated_activity)

