from fastapi import APIRouter, HTTPException, Depends, Body
from sqlmodel import Session, select
from typing import List, Optional
from database import engine
from models import (
    Service, User, Shift, ShiftLog, Operation, PaymentStatus, Role, ShiftLogAction, ShiftStatus
)
from pydantic import BaseModel
from datetime import datetime

# Роутеры
operation_router = APIRouter(prefix="/operations", tags=["operations"])
service_router = APIRouter(prefix="/services", tags=["services"])
shift_router = APIRouter(prefix="/shifts", tags=["shifts"])
user_router = APIRouter(prefix="/users", tags=["users"])
auth_router = APIRouter(prefix="/auth", tags=["auth"])

def get_session():
    with Session(engine) as session:
        yield session

# Вспомогательная функция — проверка открытой смены
def get_current_shift_for_user(operator_id: int, session: Session) -> Shift:
    shift = session.exec(
        select(Shift).where(Shift.operator_id == operator_id, Shift.end_time == None)
    ).first()
    if not shift:
        raise HTTPException(status_code=403, detail="Нет открытой смены")
    return shift

# === УСЛУГИ ===
@service_router.get("/", response_model=List[Service])
def get_services(session: Session = Depends(get_session)):
    return session.exec(select(Service)).all()

@service_router.post("/", response_model=Service)
def create_service(name: str, price: float, session: Session = Depends(get_session)):
    service = Service(name=name, price=price)
    session.add(service)
    session.commit()
    session.refresh(service)
    return service

@service_router.get("/{service_id}", response_model=Service)
def get_service(service_id: int, session: Session = Depends(get_session)):
    service = session.get(Service, service_id)
    if not service:
        raise HTTPException(404, "Услуга не найдена")
    return service

@service_router.get("/{service_id}/masters", response_model=List[User])
def get_service_masters(service_id: int, session: Session = Depends(get_session)):
    from models import MasterServiceLink
    service = session.get(Service, service_id)
    if not service:
        raise HTTPException(404, "Услуга не найдена")
    
    # Получаем всех мастеров для этой услуги через MasterServiceLink
    links = session.exec(
        select(MasterServiceLink).where(MasterServiceLink.service_id == service_id)
    ).all()
    
    master_ids = [link.master_id for link in links]
    if not master_ids:
        return []
    
    masters = session.exec(
        select(User).where(User.id.in_(master_ids), User.role == Role.MASTER)
    ).all()
    
    return masters

@service_router.post("/{service_id}/assign-master")
def assign_master_to_service(service_id: int, master_id: int, operator_id: int, session: Session = Depends(get_session)):
    from models import MasterServiceLink

    # Проверяем права оператора
    operator = session.get(User, operator_id)
    if not operator or operator.role != Role.OPERATOR:
        raise HTTPException(status_code=403, detail="Только операторы могут назначать мастеров")

    service = session.get(Service, service_id)
    if not service:
        raise HTTPException(404, "Услуга не найдена")

    master = session.get(User, master_id)
    if not master or master.role != Role.MASTER:
        raise HTTPException(400, "Мастер не найден или неверная роль")

    # Проверяем, не назначен ли уже этот мастер
    existing = session.exec(
        select(MasterServiceLink).where(
            MasterServiceLink.master_id == master_id,
            MasterServiceLink.service_id == service_id
        )
    ).first()

    if existing:
        raise HTTPException(400, "Этот мастер уже назначен на эту услугу")

    link = MasterServiceLink(master_id=master_id, service_id=service_id)
    session.add(link)
    session.commit()

    return {"message": "Мастер назначен на услугу"}

# === СМЕНЫ ===
@shift_router.post("/open")
def open_shift(operator_id: int, session: Session = Depends(get_session)):
    # Проверяем, что пользователь - оператор
    operator = session.get(User, operator_id)
    if not operator or operator.role != Role.OPERATOR:
        raise HTTPException(status_code=403, detail="Только операторы могут открывать смены")
    
    existing = session.exec(select(Shift).where(Shift.operator_id == operator_id, Shift.end_time == None)).first()
    if existing:
        raise HTTPException(400, "Смена уже открыта")

    shift = Shift(operator_id=operator_id)
    session.add(shift)
    session.commit()
    session.refresh(shift)

    log = ShiftLog(shift_id=shift.id, operator_id=operator_id, action=ShiftLogAction.OPEN)
    session.add(log)
    session.commit()

    return shift

@shift_router.get("/current")
def get_current_shift_endpoint(operator_id: int, session: Session = Depends(get_session)):
    shift = session.exec(
        select(Shift).where(Shift.operator_id == operator_id, Shift.end_time == None)
    ).first()
    if not shift:
        raise HTTPException(404, "Нет открытой смены")
    return shift

@shift_router.get("/logs", response_model=list)
def get_shift_logs(operator_id: int = None, session: Session = Depends(get_session)):
    query = select(ShiftLog)
    if operator_id:
        query = query.where(ShiftLog.operator_id == operator_id)
    # Сортируем по времени, новые сверху
    query = query.order_by(ShiftLog.timestamp.desc())
    logs = session.exec(query).all()
    
    # Возвращаем структурированные данные
    result = []
    for log in logs:
        operator = session.get(User, log.operator_id)
        shift = session.get(Shift, log.shift_id)
        result.append({
            "id": log.id,
            "shift_id": log.shift_id,
            "operator_id": log.operator_id,
            "operator_name": operator.name if operator else "Неизвестно",
            "action": log.action,
            "timestamp": log.timestamp.isoformat(),
            "shift_start": shift.start_time.isoformat() if shift else None,
            "shift_end": shift.end_time.isoformat() if shift and shift.end_time else None
        })
    return result
def close_shift(shift_id: int, operator_id: int, session: Session = Depends(get_session)):
    # Проверяем, что пользователь - оператор
    operator = session.get(User, operator_id)
    if not operator or operator.role != Role.OPERATOR:
        raise HTTPException(status_code=403, detail="Только операторы могут закрывать смены")
    
    shift = session.get(Shift, shift_id)
    if not shift or shift.operator_id != operator_id or shift.end_time:
        raise HTTPException(400, "Смена не найдена или уже закрыта")

    shift.end_time = datetime.utcnow()
    shift.status = ShiftStatus.CLOSED
    session.add(shift)
    session.commit()

    log = ShiftLog(shift_id=shift_id, operator_id=operator_id, action=ShiftLogAction.CLOSE)
    session.add(log)
    session.commit()

    return {"message": "Смена закрыта"}

# === ОПЕРАЦИИ ===
class OperationCreate(BaseModel):
    master_id: Optional[int] = None
    service_id: int
    client_name: str
    car: str
    price: float
    comment: Optional[str] = None

@operation_router.post("/", response_model=Operation)
def create_operation(
    op: OperationCreate,
    operator_id: int,
    session: Session = Depends(get_session)
):
    # Проверяем, что пользователь - оператор
    operator = session.get(User, operator_id)
    if not operator or operator.role != Role.OPERATOR:
        raise HTTPException(status_code=403, detail="Только операторы могут создавать записи")
    
    shift = get_current_shift_for_user(operator_id, session)

    operation = Operation(
        shift_id=shift.id,
        operator_id=operator_id,
        master_id=op.master_id,
        service_id=op.service_id,
        client_name=op.client_name,
        car=op.car,
        price=op.price,
        comment=op.comment
    )
    session.add(operation)
    session.commit()
    session.refresh(operation)
    return operation

@operation_router.patch("/{op_id}/pay")
def pay_operation(op_id: int, operator_id: int, session: Session = Depends(get_session)):
    # Проверяем, что пользователь - оператор или механик
    operator = session.get(User, operator_id)
    if not operator or operator.role not in [Role.OPERATOR, Role.MASTER]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    shift = get_current_shift_for_user(operator_id, session)
    operation = session.get(Operation, op_id)
    if not operation or operation.shift_id != shift.id:
        raise HTTPException(404, "Операция не найдена или не в вашей смене")
    if operation.status != PaymentStatus.PENDING:
        raise HTTPException(400, "Операция уже проведена или отменена")

    operation.status = PaymentStatus.PAID
    session.add(operation)
    session.commit()
    session.refresh(operation)
    return operation

@operation_router.patch("/{op_id}/cancel")
def cancel_operation(op_id: int, operator_id: int, reason: str = Body(...), session: Session = Depends(get_session)):
    # Проверяем, что пользователь - оператор
    operator = session.get(User, operator_id)
    if not operator or operator.role != Role.OPERATOR:
        raise HTTPException(status_code=403, detail="Только операторы могут отменять записи")
    
    shift = get_current_shift_for_user(operator_id, session)
    operation = session.get(Operation, op_id)
    if not operation or operation.shift_id != shift.id:
        raise HTTPException(404, "Операция не найдена")
    
    operation.status = PaymentStatus.CANCELLED
    operation.cancel_reason = reason
    session.add(operation)
    session.commit()
    session.refresh(operation)
    return operation

@operation_router.delete("/{op_id}")
def delete_operation(op_id: int, session: Session = Depends(get_session)):
    operation = session.get(Operation, op_id)
    if not operation:
        raise HTTPException(404, "Операция не найдена")
    
    session.delete(operation)
    session.commit()
    return {"message": "Операция удалена"}

@operation_router.get("/", response_model=List[Operation])
def get_operations(operator_id: Optional[int] = None, session: Session = Depends(get_session)):
    query = select(Operation)
    if operator_id:
        query = query.where(Operation.operator_id == operator_id)
    return session.exec(query).all()

# === ПОЛЬЗОВАТЕЛИ ===
class UserRegister(BaseModel):
    phone: str
    name: str

@user_router.get("/", response_model=List[User])
def get_users(role: str = None, session: Session = Depends(get_session)):
    query = select(User)
    if role:
        query = query.where(User.role == role)
    return session.exec(query).all()

@user_router.get("/masters", response_model=List[User])
def get_masters(session: Session = Depends(get_session)):
    return session.exec(select(User).where(User.role == Role.MASTER)).all()

@user_router.post("/register")
def register_user(user: UserRegister, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.phone == user.phone)).first()
    if existing:
        raise HTTPException(400, "Пользователь с таким телефоном уже существует")
    
    new_user = User(phone=user.phone, name=user.name, role=Role.CLIENT)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


class MasterCreate(BaseModel):
    phone: str
    name: str


@user_router.post("/create_master")
def create_master(master: MasterCreate, operator_id: int, session: Session = Depends(get_session)):
    # Только оператор может создавать мастеров
    operator = session.get(User, operator_id)
    if not operator or operator.role != Role.OPERATOR:
        raise HTTPException(status_code=403, detail="Только операторы могут добавлять мастеров")

    existing = session.exec(select(User).where(User.phone == master.phone)).first()
    if existing:
        raise HTTPException(400, "Пользователь с таким телефоном уже существует")

    new_user = User(phone=master.phone, name=master.name, role=Role.MASTER)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

class LoginRequest(BaseModel):
    phone: str

@auth_router.post("/login")
def login(request: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.phone == request.phone)).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден. Сначала зарегистрируйтесь.")

    # Имитация SMS — код всегда 1234
    code = "1234"
    print(f"КОД ДЛЯ {request.phone}: {code}")  # Увидишь в консоли uvicorn

    return {"message": "Код отправлен", "code_hint": "1234 (для теста)"}

class VerifyRequest(BaseModel):
    phone: str
    code: str

@auth_router.post("/verify")
def verify(request: VerifyRequest, session: Session = Depends(get_session)):
    if request.code != "1234":
        raise HTTPException(400, "Неверный код")

    user = session.exec(select(User).where(User.phone == request.phone)).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")

    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "phone": user.phone,
            "role": user.role
        },
        "message": "Успешный вход"
    }