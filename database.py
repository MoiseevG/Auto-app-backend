from sqlmodel import SQLModel, create_engine
import os
from dotenv import load_dotenv

load_dotenv(encoding="utf-8")

DATABASE_URL = os.getenv("DATABASE_URL")  # берём из .env

engine = create_engine(
    DATABASE_URL,
    echo=True,
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
