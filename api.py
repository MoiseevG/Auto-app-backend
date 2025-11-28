from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from typing import List
from database import engine
from models import Record, RecordCreate, RecordUpdate, RecordRead
from pydantic import BaseModel

record_router = APIRouter()

# --- Dependency: получаем сессию БД ---
def get_session():
    with Session(engine) as session:
        yield session

# --- Pydantic модель для обновления статуса оплаты ---
class PaymentStatusUpdate(BaseModel):
    payment_status: str

# --- CREATE: создание новой записи ---
@record_router.post("/", response_model=RecordRead)
def create_record(record: RecordCreate, session: Session = Depends(get_session)):
    db_record = Record(**record.dict())  
    session.add(db_record)
    session.commit()
    session.refresh(db_record)
    return db_record

# --- READ ALL: получить список всех записей ---
@record_router.get("/", response_model=List[RecordRead])
def read_records(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    records = session.exec(select(Record).offset(skip).limit(limit)).all()
    return records

# --- READ ONE: получить одну запись по ID ---
@record_router.get("/{record_id}", response_model=RecordRead)
def read_record(record_id: int, session: Session = Depends(get_session)):
    record = session.get(Record, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

# --- UPDATE: обновление записи ---
@record_router.patch("/{record_id}", response_model=RecordRead)
def update_record(record_id: int, record_update: RecordUpdate, session: Session = Depends(get_session)):
    db_record = session.get(Record, record_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    record_data = record_update.model_dump(exclude_unset=True)
    for key, value in record_data.items():
        setattr(db_record, key, value)
    
    session.add(db_record)
    session.commit()
    session.refresh(db_record)
    return db_record

# --- UPDATE PAYMENT STATUS: оплата ---
@record_router.put("/{record_id}/payment-status", response_model=RecordRead)
def update_payment_status(record_id: int, data: PaymentStatusUpdate, session: Session = Depends(get_session)):
    db_record = session.get(Record, record_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    db_record.payment_status = data.payment_status
    session.add(db_record)
    session.commit()
    session.refresh(db_record)
    return db_record

# --- DELETE: удаление записи ---
@record_router.delete("/{record_id}")
def delete_record(record_id: int, session: Session = Depends(get_session)):
    record = session.get(Record, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    session.delete(record)
    session.commit()
    return {"message": "Record deleted successfully"}
