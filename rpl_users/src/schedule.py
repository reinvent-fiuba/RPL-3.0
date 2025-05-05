import logging
from rpl_users.src.repositories.validation_tokens import ValidationTokensRepository
from rpl_users.src.deps.database import DBSessionDependency


def cleanup_validation_tokens_job():
    """
    Cleans up expired validation tokens from the database.
    This function is intended to be run weekly.
    """
    with DBSessionDependency() as db:
        validation_tokens_repo = ValidationTokensRepository(db)
        validation_tokens_repo.delete_expired_tokens()
        logging.info("Expired validation tokens cleaned up successfully.")
