from datetime import datetime, timezone

from rpl_activities.src.repositories.base import BaseRepository
import sqlalchemy as sa

from rpl_activities.src.repositories.models import aux_models
from rpl_activities.src.repositories.models.activity import Activity
from .models.activity_submission import ActivitySubmission

class SubmissionsRepository(BaseRepository):

    def get_best_submission_status_by_user_at_activity(
        self, user_id: int , activity: Activity, current_user_submissions_at_activity: list[ActivitySubmission]
    ) -> aux_models.SubmissionStatus:
        if len(current_user_submissions_at_activity) == 0:
            return aux_models.SubmissionStatus.NO_SUBMISSIONS

        statuses = [submission.status for submission in current_user_submissions_at_activity]

        status_order = list(aux_models.SubmissionStatus)
        best_status = max(
            statuses,
            key=lambda status: status_order.index(status)
        )
        return best_status
 

    def get_last_submission_date_by_user_at_activity(
        self, user_id: int , activity: Activity, current_user_submissions_at_activity: list[ActivitySubmission]
    ) -> datetime:
        if len(current_user_submissions_at_activity) == 0:
            return None
        last_submission = max(
            current_user_submissions_at_activity,
            key=lambda submission: submission.date_created
        )
        return last_submission.date_created
    

    def get_all_submissions_by_current_user_at_activities(
        self, user_id: int , activities: list[Activity]
    ):
        if len(activities) == 0:
            return []
        return (
            self.db_session.execute(
                sa.select(ActivitySubmission).where(
                    ActivitySubmission.user_id == user_id,
                    ActivitySubmission.activity_id.in_([activity.id for activity in activities]),
                )
            )
            .scalars()
            .all()
        )

    
