from sqlmodel import SQLModel, create_engine, Session
import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite:///./dev_wiki_quiz.db",
)

engine = None

def create_db_and_engine():
    global engine
    if engine is None:
        engine = create_engine(DATABASE_URL, echo=False)
        SQLModel.metadata.create_all(engine)

def get_session():
    if engine is None:
        create_db_and_engine()
    return Session(engine)
