from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from database import engine, create_db_and_tables
from api import record_router

# Lifespan для создания таблиц при старте
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables...")
    create_db_and_tables()
    print("Tables created successfully!")
    yield

# Инициализация FastAPI
app = FastAPI(
    title="Auto Service Records API",
    description="API for managing auto service records",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # адрес React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутера с префиксом
app.include_router(record_router, prefix="/api/records", tags=["records"])

# Простая проверка работы API
@app.get("/")
async def root():
    return {"message": "Auto Service Records API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Запуск через uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000, reload=True)
