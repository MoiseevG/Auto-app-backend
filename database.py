from sqlmodel import SQLModel, create_engine
import os
from dotenv import load_dotenv

load_dotenv(encoding="utf-8")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

# Для SQLite нужны специальные параметры
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        echo=True,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        DATABASE_URL,
        echo=True,
    )

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
