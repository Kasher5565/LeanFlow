from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from sqlmodel import Session, select
from database import create_db_and_tables, get_db
from sync_service import sync_service
import asyncio
from models import User, UserStatus, Task, TaskPriority, TaskStatus, Company
from datetime import date, datetime
from database import db_manager
import traceback

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

@app.get("/users/")
async def get_all_users(db: Session = Depends(get_db)):
    """Получить всех пользователей"""
    session = next(db)
    users = session.exec(select(User)).all()
    return {
        "count": len(users),
        "users": users
    }

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

@app.get("/tasks/")
async def get_all_tasks(db: Session = Depends(get_db)):
    """Получить все задачи"""
    session = next(db)
    tasks = session.exec(select(Task)).all()
    return {
        "count": len(tasks),
        "tasks": tasks
    }

# ============ ТЕСТОВЫЕ ДАННЫЕ ==============

@app.post("/test/create-sample-data")
async def create_sample_data(db: Session = Depends(get_db)):
    """Создание тестовых компаний, пользователей и задач"""
    session = next(db)
    try:
        # Создаем тестовые компании
        companies = [
            Company(
                title="ТехноСофт",
                description="IT компания по разработке ПО"
            ),
            Company(
                title="МаркетПлюс", 
                description="Маркетинговое агентство"
            )
        ]
        
        for company in companies:
            session.add(company)
        session.commit()
        
        # Получаем ID созданных компаний
        for company in companies:
            session.refresh(company)
        
        print(f"✅ Создано компаний: {len(companies)}")
        
        # Создаем тестовых пользователей
        users = [
            # Компания 1: ТехноСофт
            User(
                user_name="Иван Петров",
                email="ivan@technosoft.com",
                phone="+79161234567",
                telegram="@ivan_petrov",
                status=UserStatus.MANAGER,
                company_id=companies[0].id
            ),
            User(
                user_name="Мария Сидорова", 
                email="maria@technosoft.com",
                phone="+79167654321",
                telegram="@maria_sid",
                status=UserStatus.EMPLOYEE,
                company_id=companies[0].id
            ),
            User(
                user_name="Алексей Козлов",
                email="alex@technosoft.com", 
                status=UserStatus.EMPLOYEE,
                company_id=companies[0].id
            ),
            # Компания 2: МаркетПлюс
            User(
                user_name="Ольга Васнецова",
                email="olga@marketplus.com",
                phone="+79165556677", 
                status=UserStatus.MANAGER,
                company_id=companies[1].id
            ),
            User(
                user_name="Дмитрий Семенов",
                email="dmitry@marketplus.com",
                status=UserStatus.EMPLOYEE,
                company_id=companies[1].id
            )
        ]
        
        for user in users:
            session.add(user)
        session.commit()
        
        # Получаем ID созданных пользователей
        for user in users:
            session.refresh(user)
        
        print(f"✅ Создано пользователей: {len(users)}")
        
        # Создаем тестовые задачи
        tasks = [
            # Задачи для компании 1: ТехноСофт
            Task(
                title="Разработать главную страницу",
                description="Создать дизайн и верстку главной страницы приложения",
                assignee_id=users[1].id,  # Мария
                company_id=companies[0].id,
                due_date=date(2024, 12, 15),
                priority=TaskPriority.HIGH,
                status=TaskStatus.IN_PROGRESS
            ),
            Task(
                title="Настроить базу данных",
                description="Настроить модели и миграции базы данных",
                assignee_id=users[2].id,  # Алексей
                company_id=companies[0].id,
                due_date=date(2024, 12, 20),
                priority=TaskPriority.HIGH,
                status=TaskStatus.TODO
            ),
            Task(
                title="Протестировать API",
                description="Написать тесты для всех API эндпоинтов",
                assignee_id=users[1].id,  # Мария
                company_id=companies[0].id,
                due_date=date(2024, 12, 25),
                priority=TaskPriority.MEDIUM,
                status=TaskStatus.TODO
            ),
            # Задачи для компании 2: МаркетПлюс
            Task(
                title="Разработать маркетинговую стратегию",
                description="Создать план продвижения для нового клиента",
                assignee_id=users[4].id,  # Дмитрий
                company_id=companies[1].id,
                due_date=date(2024, 12, 10),
                priority=TaskPriority.HIGH,
                status=TaskStatus.IN_PROGRESS
            ),
            Task(
                title="Подготовить презентацию",
                description="Создать презентацию для встречи с клиентом",
                company_id=companies[1].id,  # Без исполнителя
                due_date=date(2024, 12, 12),
                priority=TaskPriority.MEDIUM,
                status=TaskStatus.TODO
            )
        ]
        
        for task in tasks:
            session.add(task)
        session.commit()
        
        print(f"✅ Создано задач: {len(tasks)}")
        
        return {
            "message": "Тестовые данные созданы!",
            "companies_created": len(companies),
            "users_created": len(users),
            "tasks_created": len(tasks),
            "online_sync": db_manager.is_online
        }
        
    except Exception as e:
        session.rollback()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка создания данных: {e}")

@app.get("/test/companies")
async def get_all_companies_test(db: Session = Depends(get_db)):
    """Получить все компании (тестовый эндпоинт)"""
    session = next(db)
    companies = session.exec(select(Company)).all()
    return {
        "count": len(companies),
        "companies": companies
    }

@app.get("/test/users")
async def get_all_users(db: Session = Depends(get_db)):
    """Получить всех пользователей"""
    session = next(db)
    users = session.exec(select(User)).all()
    return {
        "count": len(users),
        "users": users
    }

@app.get("/test/tasks")
async def get_all_tasks(db: Session = Depends(get_db)):
    """Получить все задачи"""
    session = next(db)
    tasks = session.exec(select(Task)).all()
    return {
        "count": len(tasks),
        "tasks": tasks
    }

@app.delete("/test/clear-all")
async def clear_all_data(db: Session = Depends(get_db)):
    """Очистить все данные (для тестирования)"""
    session = next(db)
    try:
        # Удаляем задачи
        tasks = session.exec(select(Task)).all()
        for task in tasks:
            session.delete(task)
        
        # Удаляем пользователей
        users = session.exec(select(User)).all()
        for user in users:
            session.delete(user)
        
        # Удаляем компании
        companies = session.exec(select(Company)).all()
        for company in companies:
            session.delete(company)
        
        session.commit()
        
        return {
            "message": "Все данные очищены",
            "tasks_deleted": len(tasks),
            "users_deleted": len(users),
            "companies_deleted": len(companies)
        }
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка очистки: {e}")