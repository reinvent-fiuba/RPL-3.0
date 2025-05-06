from .base import BaseRepository

from .models.validation_token import ValidationToken
import sqlalchemy as sa
from datetime import datetime, timedelta, timezone


class ValidationTokensRepository(BaseRepository):
    def save_new_validation_token(self, user_id: int, token: str) -> ValidationToken:
        validation_token = ValidationToken(
            user_id=user_id,
            token=token,
            expiration_date=datetime.now(timezone.utc) + timedelta(days=1),
        )
        self.db_session.add(validation_token)
        self.db_session.commit()
        self.db_session.refresh(validation_token)
        return validation_token

    def get_by_token(self, token: str) -> ValidationToken:
        return self.db_session.execute(
            sa.select(ValidationToken).where(ValidationToken.token == token)
        ).scalar_one_or_none()

    def delete_by_token(self, token: str) -> None:
        validation_token = self.get_by_token(token)
        if validation_token:
            self.db_session.delete(validation_token)
            self.db_session.commit()
