# auth.py или где у тебя роутеры
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from database import engine
from models import User

auth_router = APIRouter(prefix="/auth", tags=["auth"])

def get_session():
    with Session(engine) as session:
        yield session

@auth_router.post("/login")
async def login(phone: str = Body(...), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.phone == phone)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Имитация отправки SMS
    print(f"ТЕСТОВЫЙ КОД ДЛЯ {phone}: 1234")
    return {"message": "Код отправлен"}

@auth_router.post("/verify")
async def verify(phone: str = Body(...), code: str = Body(...), session: Session = Depends(get_session)):
    if code != "1234":
        raise HTTPException(status_code=400, detail="Неверный код")

    user = session.exec(select(User).where(User.phone == phone)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return {
        "user": {
            "id": user.id,
            "name": user.name or "Пользователь",
            "phone": user.phone,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role)
        }
    }