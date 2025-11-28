from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date
from enum import StrEnum

class PaymentStatus(StrEnum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "Cancelled"

class Record(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    client: str = Field(index=True)
    car: str = Field(index=True)
    service: str
    price: float
    date: date
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING)

class RecordCreate(SQLModel):
    client: str
    car: str
    service: str
    price: float
    date: date
    payment_status: PaymentStatus = PaymentStatus.PENDING

class RecordUpdate(SQLModel):
    client: Optional[str] = None
    car: Optional[str] = None
    service: Optional[str] = None
    price: Optional[float] = None
    date: Optional[date] = None
    payment_status: Optional[PaymentStatus] = None

class RecordRead(SQLModel):
    id: int
    client: str
    car: str
    service: str
    price: float
    date: date
    payment_status: PaymentStatus