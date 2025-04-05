from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from rpl_users.src.config.env import DB_URL


engine = create_engine(DB_URL, echo=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session():
    session: Session = SessionLocal(engine)
    try:
        yield session
    finally:
        session.close()


# This class is designed for use within the Service and Repository levels
# to facilitate the passage of the DB Session from the FastAPI Router level.
#
# This is necessary since otherwise the only way to get the DB Session into the Repository level is by passing
# it throughout the entire function tree. The DB Session is always injected at the Router level.
#
# More info:
# - https://github.com/tiangolo/fastapi/issues/2894
# - https://github.com/tiangolo/fastapi/pull/5489
class DBSessionContext:
    def __init__(self, db_session: Session):
        self.db_session = db_session
