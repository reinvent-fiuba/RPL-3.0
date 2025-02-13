import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


load_dotenv()
DB_URL = os.getenv("DB_URL")

engine = create_engine(DB_URL, echo=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session():
    session: Session = SessionLocal(engine)
    try:
        yield session
    finally:
        session.close()


# This class is designed for use in the Service and Repository levels
# to facilitate the passing of the DB Session from the FastAPI Router level.
#
# This is necessary because the DB Session is injected in the Router level,
# and the way of getting the DB Session to the Repository level is passing
# it through the function tree.
#
# More info:
# - https://github.com/tiangolo/fastapi/issues/2894
# - https://github.com/tiangolo/fastapi/pull/5489
class DBSessionContext:
    def __init__(self, db_session: Session):
        self.db_session = db_session
