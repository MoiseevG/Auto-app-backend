from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine
from api import record_router
import os
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "https://auto-app-zovz.onrender.com",
    "http://localhost:3000",
]

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)

app = FastAPI()
app.add_routeer("/records", record_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Создание таблиц при старте
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
