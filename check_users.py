from database import engine
from sqlmodel import Session, select
from models import User

with Session(engine) as session:
    users = session.exec(select(User)).all()
    print("Users in database:")
    for user in users:
        print(f"  {user.name}: {user.phone}")
