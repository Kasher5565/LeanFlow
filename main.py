from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from fastapi.security import HTTPBasicCredentials
from sqlmodel import Session, select
from database import create_db_and_tables, get_db
from sync_service import sync_service
import asyncio
from models import User, UserStatus, Task, TaskPriority, TaskStatus, Company
from datetime import date, datetime
from database import db_manager
from auth import get_current_user, hash_password, verify_password
from fastapi.security import HTTPBasic

security = HTTPBasic()

app = FastAPI(title="Task Manager")

@app.on_event("startup")
async def startup_event():
    # Инициализация базы данных
    create_db_and_tables()
    
    # Запуск фоновой синхронизации
    asyncio.create_task(sync_service.start_sync())

@app.get("/")
async def root():
    return {"message": "Task Manager API"}

@app.get("/health")
async def health_check():
    from database import db_manager
    return {
        "status": "healthy", 
        "online": db_manager.is_online,
        "supabase_connected": db_manager.is_online
    }

@app.get("/sync/now")
async def manual_sync(background_tasks: BackgroundTasks):
    """Ручной запуск синхронизации"""
    background_tasks.add_task(sync_service.sync_data)
    return {"message": "Синхронизация запущена"}

# ============ КОМПАНИИ ==============

@app.post("/companies/")
async def create_company(
    company_data: dict,
    db: Session = Depends(get_db)
):
    """Создание новой компании"""
    session = next(db)
    try:
        company = Company(
            title=company_data.get("title"),
            description=company_data.get("description")
        )
        session.add(company)
        session.commit()
        session.refresh(company)
        
        return {
            "message": "Компания создана!",
            "company": company
        }
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка создания компании: {e}")

@app.get("/companies/")
async def get_all_companies(db: Session = Depends(get_db)):
    """Получить все компании"""
    session = next(db)
    companies = session.exec(select(Company)).all()
    return {
        "count": len(companies),
        "companies": companies
    }

@app.get("/companies/{company_id}")
async def get_company(company_id: int, db: Session = Depends(get_db)):
    """Получить компанию по ID"""
    session = next(db)
    company = session.exec(
        select(Company).where(Company.id == company_id)
    ).first()
    
    if not company:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    
    return {"company": company}

# ============ ПОЛЬЗОВАТЕЛИ ==============

@app.post("/users/")
async def create_user(
    user_data: dict,
    db: Session = Depends(get_db)
):
    """Создание нового пользователя"""
    session = next(db)
    try:
        user = User(
            user_name=user_data.get("user_name"),
            email=user_data.get("email"),
            password=user_data.get("password"),
            phone=user_data.get("phone"),
            telegram=user_data.get("telegram"),
            status=user_data.get("status", UserStatus.EMPLOYEE),
            company_id=user_data.get("company_id")
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        return {
            "message": "Пользователь создан!",
            "user": user
        }
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка создания пользователя: {e}")

@app.get("/companies/{company_id}/users")
async def get_company_users(company_id: int, db: Session = Depends(get_db)):
    """Получить пользователей компании"""
    session = next(db)
    users = session.exec(
        select(User).where(User.company_id == company_id)
    ).all()
    
    return {
        "count": len(users),
        "users": users
    }

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Получить пользователя по ID"""
    session = next(db)
    
    user = session.exec(
        select(User).where(User.id == user_id)
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    user_data = user.dict()
    user_data.pop("password", None)
    
    return {"user": user_data}

# ============ ЗАДАЧИ ==============

@app.post("/tasks/")
async def create_task(
    task_data: dict,
    db: Session = Depends(get_db)
):
    """Создание новой задачи"""
    session = next(db)
    try:
        # Проверяем что исполнитель из той же компании
        if task_data.get("assignee_id"):
            assignee = session.exec(
                select(User).where(User.id == task_data.get("assignee_id"))
            ).first()
            
            if assignee and assignee.company_id != task_data.get("company_id"):
                raise HTTPException(400, "Исполнитель не из вашей компании")
        
        task = Task(
            title=task_data.get("title"),
            description=task_data.get("description"),
            assignee_id=task_data.get("assignee_id"),
            company_id=task_data.get("company_id"),
            due_date=task_data.get("due_date"),
            priority=task_data.get("priority", TaskPriority.MEDIUM),
            status=task_data.get("status", TaskStatus.TODO)
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        
        return {
            "message": "Задача создана!",
            "task": task
        }
        
    except Exception as e:
        session.rollback()
        if "Исполнитель не из вашей компании" in str(e):
            raise
        raise HTTPException(status_code=500, detail=f"Ошибка создания задачи: {e}")

@app.get("/companies/{company_id}/tasks")
async def get_company_tasks(company_id: int, db: Session = Depends(get_db)):
    """Получить задачи компании"""
    session = next(db)
    tasks = session.exec(
        select(Task).where(Task.company_id == company_id)
    ).all()
    
    return {
        "count": len(tasks),
        "tasks": tasks
    }

@app.get("/my/tasks")
async def get_my_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить задачи текущего пользователя"""
    session = next(db)
    
    tasks = session.exec(
        select(Task).where(
            (Task.company_id == current_user.company_id) &
            (Task.assignee_id == current_user.id)
        )
    ).all()
    
    return {
        "count": len(tasks),
        "tasks": tasks
    }
# ====================================================
#                  АУТЕНИФАКЦИЯ
# ====================================================

@app.post("/auth/register")
async def register(
    user_data: dict,
    db: Session = Depends(get_db)
):
    session = next(db)
    try:
        existing_user = session.exec(
            select(User).where(User.email == user_data.get("email"))
        ).first()
        
        if existing_user:
            raise HTTPException(400, "Пользователь с таким email уже существует")
        
        # Хэшируем пароль
        password_hash = hash_password(user_data.get("password", ""))
        
        # Создаем пользователя
        user = User(
            user_name=user_data.get("user_name", "Новый пользователь"),
            email=user_data.get("email"),
            password=password_hash,
            phone=user_data.get("phone"),
            telegram=user_data.get("telegram"),
            status=UserStatus.EMPLOYEE,
            company_id=user_data.get("company_id")
        )
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        return {
            "message": "Пользователь зарегистрирован!",
            "user_id": user.id,
            "user_name": user.user_name,
            "email": user.email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка регистрации: {e}")
    
@app.post("/auth/login")
async def login(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Вход пользователя"""
    session = next(db)
    
    user = session.exec(
        select(User).where(User.email == credentials.username)  # ← ИЩЕМ ПО EMAIL
    ).first()
    
    if not user:
        raise HTTPException(401, "Неверный email или пароль")
    
    # Упрощенная проверка: пароль должен быть равен email
    if not verify_password(credentials.password, user.password):
        raise HTTPException(401, "Неверный email или пароль")
    
    return {
        "message": "Успешный вход",
        "user_id": user.id,
        "user_name": user.user_name,
        "email": user.email,
        "company_id": user.company_id
    }