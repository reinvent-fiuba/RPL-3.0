from collections import defaultdict
from typing import Optional
from datetime import date
from rpl_activities.src.deps.auth import CurrentCourseUser, StudentCourseUser
from rpl_activities.src.repositories.activities import ActivitiesRepository
from rpl_activities.src.repositories.models import aux_models
from rpl_activities.src.repositories.models.activity import Activity
from rpl_activities.src.repositories.models.activity_submission import ActivitySubmission
from rpl_activities.src.repositories.submissions import SubmissionsRepository
from rpl_activities.src.services.activities import ActivitiesService
from rpl_activities.src.dtos.stats_dtos import (
    BasicActivitiesStatsOfStudentDTO,
    MetadataFoUsersGroupingDTO,
    MetadataForActivitiesGroupingDTO,
    MetadataForDateGroupingDTO,
    GroupedSubmissionsStatsDTO,
    ActivitiesStatsOfStudentDTO,
    SubmissionsStatsDTO,
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

        return ActivitiesStatsOfStudentDTO(
            amount_of_activities_started=amount_of_activities_started,
            amount_of_activities_not_started=amount_of_activities_not_started,
            amount_of_activities_solved=amount_of_activities_solved,
            points_obtained=points_obtained,
            total_possible_points=total_possible_points,
        )

    def __sum_submissions_with_specific_status(
        self, curr_user_submissions: list[ActivitySubmission], status: aux_models.SubmissionStatus
    ) -> int:
        return sum(1 for submission in curr_user_submissions if submission.status == status)

    def __calculate_and_build_stats_for_submissions(
        self,
        submissions: list[ActivitySubmission],
        total_submitters: Optional[int] = None,
        total_submitters_with_at_least_one_successful_submission: Optional[int] = None,
        total_submitters_without_successful_submissions: Optional[int] = None,
        avg_submissions_by_student: Optional[float] = None,
        avg_error_submissions_by_student: Optional[float] = None,
        avg_success_submissions_by_student: Optional[float] = None,
    ) -> SubmissionsStatsDTO:
        total_submissions = len(submissions)
        successful_submissions = self.__sum_submissions_with_specific_status(
            submissions, aux_models.SubmissionStatus.SUCCESS
        )
        submissions_with_runtime_errors = self.__sum_submissions_with_specific_status(
            submissions, aux_models.SubmissionStatus.RUNTIME_ERROR
        )
        submissions_with_build_errors = self.__sum_submissions_with_specific_status(
            submissions, aux_models.SubmissionStatus.BUILD_ERROR
        )
        submissions_with_failures = self.__sum_submissions_with_specific_status(
            submissions, aux_models.SubmissionStatus.FAILURE
        )
        return SubmissionsStatsDTO(
            total_submissions=total_submissions,
            successful_submissions=successful_submissions,
            submissions_with_runtime_errors=submissions_with_runtime_errors,
            submissions_with_build_errors=submissions_with_build_errors,
            submissions_with_failures=submissions_with_failures,
            avg_submissions_by_student=avg_submissions_by_student,
            avg_error_submissions_by_student=avg_error_submissions_by_student,
            avg_success_submissions_by_student=avg_success_submissions_by_student,
            total_submitters=total_submitters,
            total_submitters_with_at_least_one_successful_submission=total_submitters_with_at_least_one_successful_submission,
            total_submitters_without_successful_submissions=total_submitters_without_successful_submissions,
        )

    # ==============================================================================

    def get_basic_activities_stats_for_users(
        self, course_id: int, current_course_user: CurrentCourseUser, user_ids: Optional[list[int]] = None
    ) -> list[BasicActivitiesStatsOfStudentDTO]:
        self.activities_service.verify_permission_to_view(current_course_user)
        if not user_ids:
            return []
        activities = self.activities_repo.get_all_active_activities_by_course_id(course_id)
        all_submissions = self.submissions_repo.get_all_submissions_by_users_at_activities(
            user_ids, activities
        )
        submissions_by_user = defaultdict(list)
        for submission in all_submissions:
            submissions_by_user[submission.user_id].append(submission)
        basic_stats = []
        for user_id in user_ids:
            user_submissions = submissions_by_user.get(user_id, [])
            successful_submissions = [
                submission
                for submission in user_submissions
                if submission.status == aux_models.SubmissionStatus.SUCCESS
            ]
            activities_with_at_least_one_success = set(
                submission.activity for submission in successful_submissions
            )
            basic_stats.append(
                BasicActivitiesStatsOfStudentDTO(
                    user_id=user_id,
                    total_score=sum(activity.points for activity in activities_with_at_least_one_success),
                    successful_activities_count=len(activities_with_at_least_one_success),
                )
            )
        return basic_stats

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
    ) -> SubmissionsStatsDTO:
        self.activities_service.verify_permission_to_submit(current_course_user)
        activities = self.activities_repo.get_all_active_activities_by_course_id(course_id)
        curr_user_submissions = self.submissions_repo.get_all_submissions_by_user_at_activities(
            current_course_user.user_id, activities
        )
        return self.__calculate_and_build_stats_for_submissions(curr_user_submissions)

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
    ) -> GroupedSubmissionsStatsDTO:
        self.activities_service.verify_permission_to_manage(current_course_user)

        activities = self.__get_activities_with_filters_applied(course_id, category_id, activity_id)
        students = self.__get_students_with_filter_applied(all_students_course_users, user_id)

        if group_by == "user":
            return self.__get_submission_stats_grouped_by_user(students, activities, date)
        elif group_by == "date":
            return self.__get_submission_stats_grouped_by_date(students, activities, date)
        else:
            return self.__get_submission_stats_grouped_by_activity(students, activities, date)

    def __get_activities_with_filters_applied(
        self, course_id: int, category_id: Optional[int], activity_id: Optional[int]
    ) -> list[Activity]:
        activities = self.activities_repo.get_all_active_activities_by_course_id(course_id)
        if category_id is not None:
            activities = [act for act in activities if act.category_id == category_id]
        if activity_id is not None:
            activities = [act for act in activities if act.id == activity_id]
        return activities

    def __get_students_with_filter_applied(
        self, all_students_course_users: list[StudentCourseUser], user_id: Optional[int]
    ) -> list[StudentCourseUser]:
        if user_id is not None:
            return [student for student in all_students_course_users if student.user_id == user_id]
        return all_students_course_users

    def __get_submission_stats_grouped_by_user(
        self, students: list[StudentCourseUser], activities: list[Activity], date_filter: Optional[date]
    ) -> GroupedSubmissionsStatsDTO:
        submissions_by_user_id = self.__gather_submissions_grouped_by_user_id(
            students, activities, date_filter
        )
        students_by_user_id = {student.user_id: student for student in students}
        stats_sorted_by_user_grouped = []
        grouping_metadata = []
        for user_id, submissions in submissions_by_user_id.items():
            stats = self.__calculate_submissions_stats(students, submissions, submissions_by_user_id)
            stats_sorted_by_user_grouped.append(stats)
            student = students_by_user_id.get(user_id)
            if student:
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
        return GroupedSubmissionsStatsDTO(
            submissions_stats=stats_sorted_by_user_grouped, metadata=grouping_metadata
        )

    def __get_submission_stats_grouped_by_date(
        self, students: list[StudentCourseUser], activities: list[Activity], date_filter: Optional[date]
    ) -> GroupedSubmissionsStatsDTO:
        submissions_by_date = self.__gather_submissions_grouped_by_date(students, activities, date_filter)
        stats_sorted_by_date_grouped = []
        grouping_metadata = []
        for grouping_date, submissions in submissions_by_date.items():
            stats = self.__calculate_submissions_stats(students, submissions)
            stats_sorted_by_date_grouped.append(stats)
            grouping_metadata.append(MetadataForDateGroupingDTO(date=grouping_date))
        return GroupedSubmissionsStatsDTO(
            submissions_stats=stats_sorted_by_date_grouped, metadata=grouping_metadata
        )

    def __get_submission_stats_grouped_by_activity(
        self, students: list[StudentCourseUser], activities: list[Activity], date_filter: Optional[date]
    ) -> GroupedSubmissionsStatsDTO:
        submissions_by_activity = self.__gather_submissions_grouped_by_activity(
            students, activities, date_filter
        )
        stats_sorted_by_activity_grouped = []
        grouping_metadata = []
        for activity, submissions in submissions_by_activity.items():
            stats = self.__calculate_submissions_stats(students, submissions)
            stats_sorted_by_activity_grouped.append(stats)
            grouping_metadata.append(
                MetadataForActivitiesGroupingDTO(
                    id=activity.id,
                    name=activity.name,
                    points=activity.points,
                    category_name=activity.category.name,
                )
            )
        return GroupedSubmissionsStatsDTO(
            submissions_stats=stats_sorted_by_activity_grouped, metadata=grouping_metadata
        )

    def __calculate_submissions_stats(
        self,
        students: list[StudentCourseUser],
        submissions: list[ActivitySubmission],
        grouped_submissions_by_user_id: Optional[dict[int, list[ActivitySubmission]]] = None,
    ) -> SubmissionsStatsDTO:
        total_submitters = 0
        total_submitters_with_at_least_one_successful_submission = 0
        total_submitters_without_successful_submissions = 0

        total_submissions = 0
        total_submissions_with_success = 0
        total_submissions_with_error = 0

        if grouped_submissions_by_user_id is None:
            grouped_submissions_by_user_id = defaultdict(list[ActivitySubmission])
            for submission in submissions:
                grouped_submissions_by_user_id[submission.user_id].append(submission)
            for student in students:
                grouped_submissions_by_user_id[student.user_id] = grouped_submissions_by_user_id.get(
                    student.user_id, []
                )

        for user_id, user_submissions in grouped_submissions_by_user_id.items():
            if user_submissions:
                total_submitters += 1
                total_submissions_with_success += sum(
                    1
                    for submission in user_submissions
                    if submission.status == aux_models.SubmissionStatus.SUCCESS
                )
                total_submissions_with_error += sum(
                    1
                    for submission in user_submissions
                    if submission.status != aux_models.SubmissionStatus.SUCCESS
                )
                total_submissions += len(user_submissions)
                if any(
                    submission.status == aux_models.SubmissionStatus.SUCCESS
                    for submission in user_submissions
                ):
                    total_submitters_with_at_least_one_successful_submission += 1
                else:
                    total_submitters_without_successful_submissions += 1

        avg_submissions_by_student = total_submissions / total_submitters if total_submitters > 0 else 0
        avg_error_submissions_by_student = (
            total_submissions_with_error / total_submitters if total_submitters > 0 else 0
        )
        avg_success_submissions_by_student = (
            total_submissions_with_success / total_submitters if total_submitters > 0 else 0
        )
        return self.__calculate_and_build_stats_for_submissions(
            submissions,
            total_submitters,
            total_submitters_with_at_least_one_successful_submission,
            total_submitters_without_successful_submissions,
            avg_submissions_by_student,
            avg_error_submissions_by_student,
            avg_success_submissions_by_student,
        )

    # ==============================================================================

    def __gather_submissions_grouped_by_user_id(
        self, students: list[StudentCourseUser], activities: list[Activity], date_filter: Optional[date]
    ) -> dict[int, list[ActivitySubmission]]:
        submissions_by_user_id = defaultdict(list[ActivitySubmission])
        submissions = self.__get_all_submissions_by_students_at_activities(students, activities, date_filter)
        for submission in submissions:
            submissions_by_user_id[submission.user_id].append(submission)
        for student in students:
            submissions_by_user_id[student.user_id] = submissions_by_user_id.get(student.user_id, [])
        return submissions_by_user_id

    def __gather_submissions_grouped_by_date(
        self, students: list[StudentCourseUser], activities: list[Activity], date_filter: Optional[date]
    ) -> dict[date, list[ActivitySubmission]]:
        submissions_by_date = defaultdict(list[ActivitySubmission])
        submissions = self.__get_all_submissions_by_students_at_activities(students, activities, date_filter)
        for submission in submissions:
            submission_date = submission.date_created.date()
            submissions_by_date[submission_date].append(submission)
        return submissions_by_date

    def __gather_submissions_grouped_by_activity(
        self, students: list[StudentCourseUser], activities: list[Activity], date_filter: Optional[date]
    ) -> dict[Activity, list[ActivitySubmission]]:
        submissions_by_activity = defaultdict(list[ActivitySubmission])
        submissions = self.__get_all_submissions_by_students_at_activities(students, activities, date_filter)
        for submission in submissions:
            submissions_by_activity[submission.activity].append(submission)
        for activity in activities:
            submissions_by_activity[activity] = submissions_by_activity.get(activity, [])
        return submissions_by_activity

    def __get_all_submissions_by_students_at_activities(
        self, students: list[StudentCourseUser], activities: list[Activity], date_filter: Optional[date]
    ) -> list[ActivitySubmission]:
        user_ids = [student.user_id for student in students]
        submissions = self.submissions_repo.get_all_submissions_by_users_at_activities(user_ids, activities)
        if date_filter:
            submissions = [
                submission for submission in submissions if submission.date_created.date() == date_filter
            ]
        return submissions
