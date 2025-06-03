from collections import defaultdict
from typing import Optional
from datetime import date
from rpl_activities.src.deps.auth import CurrentCourseUser, StudentCourseUser
from rpl_activities.src.repositories.activities import ActivitiesRepository
from rpl_activities.src.repositories.models import aux_models
from rpl_activities.src.repositories.models.activity import Activity
from rpl_activities.src.repositories.models.activity_submission import (
    ActivitySubmission,
)
from rpl_activities.src.repositories.submissions import SubmissionsRepository
from rpl_activities.src.services.activities import ActivitiesService
from rpl_activities.src.dtos.stats_dtos import (
    MetadataFoUsersGroupingDTO,
    MetadataForActivitiesGroupingDTO,
    MetadataForDateGroupingDTO,
    SubmissionsStatsOfCourseDTO,
    ActivitiesStatsOfStudentDTO,
    SubmissionsStatsOfStudentDTO,
)


class StatsService:
    def __init__(self, db):
        self.submissions_repo = SubmissionsRepository(db)
        self.activities_service = ActivitiesService(db)
        self.activities_repo = ActivitiesRepository(db)

    def __group_current_user_submissions_by_activity(
        self, current_user_submissions: list[ActivitySubmission]
    ) -> dict[int, list[ActivitySubmission]]:
        curr_user_submissions_grouped_by_activity: dict[int, list[ActivitySubmission]] = {}
        for submission in current_user_submissions:
            activity_id = submission.activity_id
            if activity_id not in curr_user_submissions_grouped_by_activity:
                curr_user_submissions_grouped_by_activity[activity_id] = []
            curr_user_submissions_grouped_by_activity[activity_id].append(submission)
        return curr_user_submissions_grouped_by_activity

    # If one result is None, the rest will also be None.
    # This function returns:
    # - name of activity with the most failed attempts
    # - amount of failed attempts for that activity
    # - average failed attempts per activity
    def __get_detailed_stats_related_to_failed_attempts(
        self,
        activities: list[Activity],
        curr_user_submissions_grouped_by_activity: dict[int, list[ActivitySubmission]],
    ) -> tuple[Optional[str], Optional[int], Optional[float]]:
        if not activities or not curr_user_submissions_grouped_by_activity:
            return None, None, None
        name_of_activity_with_the_most_failed_attempts = None
        amount_of_failed_attempts_for_activity_with_the_most_failed_attempts = None

        current_max_failed_attempts = 0
        total_failed_attempts = 0
        counted_activities = 0

        for activity in activities:
            submissions = curr_user_submissions_grouped_by_activity.get(activity.id)
            if not submissions:
                continue
            failed_attempts_for_this_activity = sum(
                1
                for submission in submissions
                if submission.status
                in [
                    aux_models.SubmissionStatus.RUNTIME_ERROR,
                    aux_models.SubmissionStatus.BUILD_ERROR,
                    aux_models.SubmissionStatus.FAILURE,
                ]
            )
            total_failed_attempts += failed_attempts_for_this_activity
            counted_activities += 1
            if failed_attempts_for_this_activity > current_max_failed_attempts:
                current_max_failed_attempts = failed_attempts_for_this_activity
                name_of_activity_with_the_most_failed_attempts = activity.name
                amount_of_failed_attempts_for_activity_with_the_most_failed_attempts = (
                    failed_attempts_for_this_activity
                )

        average_failed_attempts_per_activity = (
            total_failed_attempts / counted_activities if counted_activities > 0 else None
        )

        return (
            name_of_activity_with_the_most_failed_attempts,
            amount_of_failed_attempts_for_activity_with_the_most_failed_attempts,
            average_failed_attempts_per_activity,
        )

    def __calculate_activities_stats_of_current_user(
        self,
        activities: list[Activity],
        curr_user_submissions_grouped_by_activity: dict[int, list[ActivitySubmission]],
    ) -> ActivitiesStatsOfStudentDTO:
        amount_of_activities_started = 0
        amount_of_activities_not_started = 0
        amount_of_activities_solved = 0
        points_obtained = 0
        total_possible_points = 0

        for activity in activities:
            submissions = curr_user_submissions_grouped_by_activity.get(activity.id, [])
            total_possible_points += activity.points
            if not submissions:
                amount_of_activities_not_started += 1
            elif any(submission.status == aux_models.SubmissionStatus.SUCCESS for submission in submissions):
                amount_of_activities_solved += 1
                points_obtained += activity.points
            else:
                amount_of_activities_started += 1

        (
            name_of_activity_with_the_most_failed_attempts,
            amount_of_failed_attempts_for_activity_with_the_most_failed_attempts,
            average_failed_attempts_per_activity,
        ) = self.__get_detailed_stats_related_to_failed_attempts(
            activities,
            curr_user_submissions_grouped_by_activity,
        )
        return ActivitiesStatsOfStudentDTO(
            amount_of_activities_started,
            amount_of_activities_not_started,
            amount_of_activities_solved,
            points_obtained,
            total_possible_points,
            name_of_activity_with_the_most_failed_attempts,
            amount_of_failed_attempts_for_activity_with_the_most_failed_attempts,
            average_failed_attempts_per_activity,
        )

    def __sum_submissions_with_specific_status(
        self,
        curr_user_submissions: list[ActivitySubmission],
        status: aux_models.SubmissionStatus,
    ) -> int:
        return sum(1 for submission in curr_user_submissions if submission.status == status)

    def __calculate_submissions_stats_of_current_user(
        self,
        activities: list[Activity],
        curr_user_submissions: list[ActivitySubmission],
        curr_user_submissions_grouped_by_activity: dict[int, list[ActivitySubmission]],
    ) -> SubmissionsStatsOfStudentDTO:
        total_submissions = len(curr_user_submissions)
        successful_submissions = self.__sum_submissions_with_specific_status(
            curr_user_submissions, aux_models.SubmissionStatus.SUCCESS
        )
        submissions_with_runtime_errors = self.__sum_submissions_with_specific_status(
            curr_user_submissions, aux_models.SubmissionStatus.RUNTIME_ERROR
        )
        submissions_with_build_errors = self.__sum_submissions_with_specific_status(
            curr_user_submissions, aux_models.SubmissionStatus.BUILD_ERROR
        )
        submissions_with_failures = self.__sum_submissions_with_specific_status(
            curr_user_submissions, aux_models.SubmissionStatus.FAILURE
        )
        (
            name_of_activity_with_the_most_failed_attempts,
            amount_of_failed_attempts_for_activity_with_the_most_failed_attempts,
            average_failed_attempts_per_activity,
        ) = self.__get_detailed_stats_related_to_failed_attempts(
            activities,
            curr_user_submissions_grouped_by_activity,
        )
        return SubmissionsStatsOfStudentDTO(
            total_submissions,
            successful_submissions,
            submissions_with_runtime_errors,
            submissions_with_build_errors,
            submissions_with_failures,
            name_of_activity_with_the_most_failed_attempts,
            amount_of_failed_attempts_for_activity_with_the_most_failed_attempts,
            average_failed_attempts_per_activity,
        )

    # ==============================================================================

    def get_activities_stats_for_current_user(
        self, course_id: int, current_course_user: CurrentCourseUser
    ) -> ActivitiesStatsOfStudentDTO:
        self.activities_service.verify_permission_to_submit(current_course_user)
        activities = self.activities_repo.get_all_active_activities_by_course_id(course_id)
        curr_user_submissions = self.submissions_repo.get_all_submissions_by_user_at_activities(
            current_course_user.user_id, activities
        )
        curr_user_submissions_grouped_by_activity = self.__group_current_user_submissions_by_activity(
            curr_user_submissions
        )
        return self.__calculate_activities_stats_of_current_user(
            activities, curr_user_submissions_grouped_by_activity
        )

    def get_submissions_stats_for_current_user(
        self, course_id: int, current_course_user: CurrentCourseUser
    ) -> SubmissionsStatsOfStudentDTO:
        self.activities_service.verify_permission_to_submit(current_course_user)
        activities = self.activities_repo.get_all_active_activities_by_course_id(course_id)
        curr_user_submissions = self.submissions_repo.get_all_submissions_by_user_at_activities(
            current_course_user.user_id, activities
        )
        curr_user_submissions_grouped_by_activity = self.__group_current_user_submissions_by_activity(
            curr_user_submissions
        )
        return self.__calculate_submissions_stats_of_current_user(
            activities, curr_user_submissions, curr_user_submissions_grouped_by_activity
        )

    # ==============================================================================

    def get_submissions_stats_for_students_according_to_filters(
        self,
        current_course_user: CurrentCourseUser,
        all_students_course_users: list[StudentCourseUser],
        course_id: int,
        date: Optional[date],
        category_id: Optional[int],
        user_id: Optional[int],
        activity_id: Optional[int],
        group_by: Optional[str],
    ) -> SubmissionsStatsOfCourseDTO:
        self.activities_service.verify_permission_to_manage(current_course_user)

        activities = self.__get_activities_with_filters_applied(course_id)
        students = self.__get_students_with_filter_applied(all_students_course_users, user_id)

        if group_by == "user":
            return self.__get_submission_stats_grouped_by_user(students, activities, date)
        elif group_by == "date":
            return self.__get_submission_stats_grouped_by_date(students, activities, date)
        else:
            return self.__get_submission_stats_grouped_by_activity(students, activities, date)

    # ==============================================================================

    def __get_activities_with_filters_applied(
        self,
        course_id: int,
        category_id: Optional[int],
        activity_id: Optional[int],
    ) -> list[Activity]:
        activities = self.activities_repo.get_all_active_activities_by_course_id(course_id)
        if category_id is not None:
            activities = [act for act in activities if act.category_id == category_id]
        if activity_id is not None:
            activities = [act for act in activities if act.id == activity_id]
        return activities

    def __get_students_with_filter_applied(
        self,
        all_students_course_users: list[StudentCourseUser],
        user_id: Optional[int],
    ) -> list[StudentCourseUser]:
        if user_id is not None:
            return [student for student in all_students_course_users if student.user_id == user_id]
        return all_students_course_users

    def __get_submission_stats_grouped_by_activity(
        self,
        students: list[StudentCourseUser],
        activities: list[Activity],
        date_filter: Optional[date],
    ) -> SubmissionsStatsOfCourseDTO:
        stats_sorted_by_activity_grouped = []
        grouping_metadata = []
        submitters = set()
        submitters_with_one_success = set()
        course_submissions_count = 0
        course_successful_submissions_count = 0
        course_errored_submissions_count = 0

        for activity in activities:
            filtered_submissions_for_activity = self.__get_filtered_submissions_for_activity(
                activity,
                students,
                date_filter,
                submitters,
                submitters_with_one_success,
            )
            stats = self.__calculate_submissions_stats_of_current_user(
                [activity],
                filtered_submissions_for_activity,
                self.__group_current_user_submissions_by_activity(filtered_submissions_for_activity),
            )
            stats_sorted_by_activity_grouped.append(stats)
            grouping_metadata.append(
                MetadataForActivitiesGroupingDTO(
                    id=activity.id,
                    name=activity.name,
                    points=activity.points,
                    category_name=activity.category.name,
                )
            )
            course_submissions_count += stats.total_submissions
            course_successful_submissions_count += stats.successful_submissions
            course_errored_submissions_count += (
                stats.submissions_with_runtime_errors
                + stats.submissions_with_build_errors
                + stats.submissions_with_failures
            )

        return SubmissionsStatsOfCourseDTO(
            stats_per_student=stats_sorted_by_activity_grouped,
            grouping_metadata=grouping_metadata,
            total_submitters=len(submitters),
            total_submitters_with_at_least_one_successful_submission=len(submitters_with_one_success),
            total_submissions_of_all_students=course_submissions_count,
            total_successful_submissions_of_all_students=course_successful_submissions_count,
            total_errored_submissions_of_all_students=course_errored_submissions_count,
        )

    def __get_submission_stats_grouped_by_user(
        self,
        students: list[StudentCourseUser],
        activities: list[Activity],
        date_filter: Optional[date],
    ) -> SubmissionsStatsOfCourseDTO:
        stats_sorted_by_user_grouped = []
        grouping_metadata = []
        total_submitters_count = 0
        total_submitters_with_success_count = 0
        course_submissions_count = 0
        course_successful_submissions_count = 0
        course_errored_submissions_count = 0

        for student in students:
            filtered_submissions_for_student = self.__get_filtered_submissions_for_student(
                student, activities, date_filter
            )
            if filtered_submissions_for_student:
                total_submitters_count += 1
            if any(
                submission.status == aux_models.SubmissionStatus.SUCCESS
                for submission in filtered_submissions_for_student
            ):
                total_submitters_with_success_count += 1
            stats = self.__calculate_submissions_stats_of_current_user(
                activities,
                filtered_submissions_for_student,
                self.__group_current_user_submissions_by_activity(filtered_submissions_for_student),
            )
            stats_sorted_by_user_grouped.append(stats)
            grouping_metadata.append(
                MetadataFoUsersGroupingDTO(
                    id=student.user_id,
                    course_user_id=student.id,
                    name=student.name,
                    surname=student.surname,
                    username=student.username,
                    student_id=student.student_id,
                )
            )
            course_submissions_count += stats.total_submissions
            course_successful_submissions_count += stats.successful_submissions
            course_errored_submissions_count += (
                stats.submissions_with_runtime_errors
                + stats.submissions_with_build_errors
                + stats.submissions_with_failures
            )

        return SubmissionsStatsOfCourseDTO(
            stats_per_student=stats_sorted_by_user_grouped,
            grouping_metadata=grouping_metadata,
            total_submitters=total_submitters_count,
            total_submitters_with_at_least_one_successful_submission=total_submitters_with_success_count,
            total_submissions_of_all_students=course_submissions_count,
            total_successful_submissions_of_all_students=course_successful_submissions_count,
            total_errored_submissions_of_all_students=course_errored_submissions_count,
        )

    def __get_submission_stats_grouped_by_date(
        self,
        students: list[StudentCourseUser],
        activities: list[Activity],
        date_filter: Optional[date],
    ) -> SubmissionsStatsOfCourseDTO:
        submissions_by_date = self.__gather_submissions_grouped_by_date(students, activities, date_filter)

        stats_sorted_by_date_grouped = []
        grouping_metadata = []
        total_submitters = set()
        total_submitters_with_success = set()
        course_submissions_count = 0
        course_successful_submissions_count = 0
        course_errored_submissions_count = 0

        for submission_date, submissions_on_date in sorted(submissions_by_date.items()):
            users_on_date = set(submission.user_id for submission in submissions_on_date)
            total_submitters.update(users_on_date)
            if any(
                submission.status == aux_models.SubmissionStatus.SUCCESS for submission in submissions_on_date
            ):
                total_submitters_with_success.update(users_on_date)
            stats = self.__calculate_submissions_stats_of_current_user(
                activities,
                submissions_on_date,
                self.__group_current_user_submissions_by_activity(submissions_on_date),
            )
            stats_sorted_by_date_grouped.append(stats)
            grouping_metadata.append(MetadataForDateGroupingDTO(date=submission_date))
            course_submissions_count += stats.total_submissions
            course_successful_submissions_count += stats.successful_submissions
            course_errored_submissions_count += (
                stats.submissions_with_runtime_errors
                + stats.submissions_with_build_errors
                + stats.submissions_with_failures
            )

        return SubmissionsStatsOfCourseDTO(
            stats_per_student=stats_sorted_by_date_grouped,
            grouping_metadata=grouping_metadata,
            total_submitters=len(total_submitters),
            total_submitters_with_at_least_one_successful_submission=len(total_submitters_with_success),
            total_submissions_of_all_students=course_submissions_count,
            total_successful_submissions_of_all_students=course_successful_submissions_count,
            total_errored_submissions_of_all_students=course_errored_submissions_count,
        )

    def __get_filtered_submissions_for_activity(
        self,
        activity: Activity,
        students: list[StudentCourseUser],
        date_filter: Optional[date],
        total_submitters_set: set,
        total_submitters_with_success_set: set,
    ) -> list[ActivitySubmission]:
        filtered_submissions = []
        for student in students:
            submissions_for_student = self.submissions_repo.get_all_submissions_from_activity_id_and_user_id(
                activity.id, student.user_id
            )
            if date_filter:
                submissions_for_student = [
                    submission
                    for submission in submissions_for_student
                    if submission.date_created.date() == date_filter
                ]
            if submissions_for_student:
                total_submitters_set.add(student.user_id)
            if any(
                submission.status == aux_models.SubmissionStatus.SUCCESS
                for submission in submissions_for_student
            ):
                total_submitters_with_success_set.add(student.user_id)
            filtered_submissions.extend(submissions_for_student)
        return filtered_submissions

    def __get_filtered_submissions_for_student(
        self,
        student: StudentCourseUser,
        activities: list[Activity],
        date_filter: Optional[date],
    ) -> list[ActivitySubmission]:
        filtered_submissions = []
        for activity in activities:
            submissions_for_activity = self.submissions_repo.get_all_submissions_from_activity_id_and_user_id(
                activity.id, student.user_id
            )
            if date_filter:
                submissions_for_activity = [
                    submission
                    for submission in submissions_for_activity
                    if submission.date_created.date() == date_filter
                ]
            filtered_submissions.extend(submissions_for_activity)
        return filtered_submissions

    def __gather_submissions_grouped_by_date(
        self,
        students: list[StudentCourseUser],
        activities: list[Activity],
        date_filter: Optional[date],
    ) -> dict[date, list[ActivitySubmission]]:
        submissions_by_date = defaultdict(list)
        for student in students:
            for activity in activities:
                submissions_for_activity = (
                    self.submissions_repo.get_all_submissions_from_activity_id_and_user_id(
                        activity.id, student.user_id
                    )
                )
                for submission in submissions_for_activity:
                    submission_date = submission.date_created.date()
                    if date_filter and submission_date != date_filter:
                        continue
                    submissions_by_date[submission_date].append(submission)
        return submissions_by_date
