from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from rpl_activities.src.config.env import DB_URL
from typing import Annotated
from fastapi import Depends


engine = create_engine(DB_URL, echo=True, pool_recycle=3600)
SessionLocal = sessionmaker(autoflush=False, bind=engine)

# Dependency =============================


def get_db_session():
    session: Session = SessionLocal(engine)
    try:
        yield session
    finally:
        session.close()


DBSessionDependency = Annotated[Session, Depends(get_db_session)]

# ==========================================
