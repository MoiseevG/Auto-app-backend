from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Импортируем все роутеры из api.py
from api import (
    operation_router,
    service_router,
    shift_router,
    user_router,
    auth_router
)
from database import create_db_and_tables
from init_db import init_test_data

app = FastAPI(title="Автосервис CRM", version="1.0")

# Создаем таблицы и инициализируем данные при запуске
create_db_and_tables()
try:
    init_test_data()
except Exception as e:
    print(f"Инициализация данных: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth_router)       
app.include_router(user_router)      
app.include_router(service_router)    
app.include_router(shift_router)     
app.include_router(operation_router)  
 

@app.get("/")
def root():
    return {"message": "Автосервис CRM API работает! 🚀"}

@app.get("/health")
def health():
    return {"status": "ok"}