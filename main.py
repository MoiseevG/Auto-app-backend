from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, create_engine
from api import record_router
import os



DATABASE_URL = os.getenv("DATABASE_URL") + "?sslmode=require"  # Добавьте параметр
engine = create_engine(DATABASE_URL, echo=True)
app = FastAPI()

origins = [
    "https://auto-app-zovz.onrender.com",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(record_router, prefix="/records")


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
