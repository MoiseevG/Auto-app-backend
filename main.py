from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine

import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)

app = FastAPI()

# Создание таблиц при старте
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
