import os
from dotenv import load_dotenv
from sqlmodel import Session, create_engine

# TODO: We no longer use SQLModel but SQLAlchemy directly for better control over the orm and its classes. Change the engine creation


load_dotenv()
DB_URL = os.getenv("DB_URL")

engine = create_engine(DB_URL, echo=True)


def get_db():
    with Session(engine) as session:
        yield session


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
