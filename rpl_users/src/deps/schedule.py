import logging
from rpl_users.src.repositories.validation_tokens import ValidationTokensRepository
from rpl_users.src.deps.database import get_db_session


def cleanup_validation_tokens_job():
    with get_db_session() as db_session:
        validation_tokens_repo = ValidationTokensRepository(db_session)
        validation_tokens_repo.delete_expired_tokens()
        logging.info("Expired validation tokens cleaned up successfully.")
