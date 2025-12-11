from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import StrEnum

class PaymentStatus(StrEnum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"

class Role(StrEnum):
    OPERATOR = "operator"
    MASTER = "master"
    CLIENT = "client"

# Услуга
class Service(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    price: float

# Пользователь
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    phone: str = Field(index=True, unique=True)
    role: Role

# Смена
class ShiftStatus(StrEnum):
    OPEN = "open"
    CLOSED = "closed"

class Shift(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    operator_id: int = Field(foreign_key="user.id")
    status: ShiftStatus = ShiftStatus.OPEN
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None

    @property
    def is_open(self) -> bool:
        return self.end_time is None

# Лог смены
class ShiftLogAction(StrEnum):
    OPEN = "open"
    CLOSE = "close"

class ShiftLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    shift_id: int = Field(foreign_key="shift.id")
    operator_id: int = Field(foreign_key="user.id")
    action: ShiftLogAction
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Операция
class Operation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    shift_id: int = Field(foreign_key="shift.id")
    operator_id: int = Field(foreign_key="user.id")
    master_id: Optional[int] = Field(default=None, foreign_key="user.id")
    service_id: int = Field(foreign_key="service.id")
    
    client_name: str
    car: str
    price: float
    status: PaymentStatus = PaymentStatus.PENDING
    comment: Optional[str] = None
    cancel_reason: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)

# Связь мастер ↔ услуга
class MasterServiceLink(SQLModel, table=True):
    master_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    service_id: Optional[int] = Field(default=None, foreign_key="service.id", primary_key=True)