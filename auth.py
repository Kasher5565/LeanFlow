# auth.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlmodel import Session, select
from database import get_db
from models import User
import bcrypt

security = HTTPBasic()

def hash_password(password: str) -> str:
    """Хэширование пароля"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

async def get_current_user(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Получаем текущего пользователя по email и паролю"""
    session = next(db)
    
    user = session.exec(
        select(User).where(User.email == credentials.username) 
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # Проверяем пароль
    if not verify_password(credentials.password, user.password): 
        raise HTTPException(
            status_code=401,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return user