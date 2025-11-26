from sqlmodel import SQLModel, create_engine
import os
from dotenv import load_dotenv

load_dotenv(encoding="utf-8")

DATABASE_URL = "postgresql://postgres:123@localhost:5432/autoservice_db"

engine = create_engine(
    DATABASE_URL,
    echo=True,
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
