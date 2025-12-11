"""
Инициализация БД с тестовыми данными
"""
import os
import sys
from database import engine, create_db_and_tables, DATABASE_URL
from sqlmodel import Session, select
from models import User, Service, Role

# Для Windows - устанавливаем кодировку консоли
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def database_exists():
    """Проверяет, существует ли файл базы данных"""
    if DATABASE_URL.startswith("sqlite"):
        # Извлекаем путь из SQLite URL
        db_path = DATABASE_URL.replace("sqlite:///./", "").replace("sqlite:///", "")
        return os.path.exists(db_path)
    # Для других БД (PostgreSQL и т.д.) считаем, что БД существует
    return True

def init_test_data():
    """Создает таблицы и добавляет тестовые данные"""
    db_exists = database_exists()
    
    # Создаем таблицы (безопасно, если они уже есть)
    create_db_and_tables()
    
    with Session(engine) as session:
        # Проверяем, есть ли уже пользователи
        existing_users = session.exec(select(User)).all()
        if existing_users:
            print(f"[OK] База данных уже инициализирована ({len(existing_users)} пользователей). Пропускаем...")
            return
        
        # Создаем тестовых пользователей
        users = [
            User(name="Иван Петров", phone="+79991112233", role=Role.OPERATOR),
            User(name="Сергей Сидоров", phone="+79992223344", role=Role.MASTER),
            User(name="Клиент Иванов", phone="+79993334455", role=Role.CLIENT),
        ]
        
        for user in users:
            session.add(user)
        
        session.commit()
        print(f"[OK] Добавлено {len(users)} пользователей")
        
        # Создаем услуги
        services = [
            Service(name="Замена масла", price=2500),
            Service(name="Замена фильтров", price=1500),
            Service(name="Диагностика", price=500),
            Service(name="Полировка", price=5000),
        ]
        
        for service in services:
            session.add(service)
        
        session.commit()
        print(f"[OK] Добавлено {len(services)} услуг")

if __name__ == "__main__":
    init_test_data()
