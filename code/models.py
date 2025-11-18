from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
from pydantic import EmailStr

# Модели связанные с задачами

# Статусы задач
class TaskStatus(str, Enum):
    TODO = "Надо сделать"
    IN_PROGRESS = "В процессе"
    DONE = "Выполнена"

class TaskPriority(str, Enum):
    LOW = "Низкий"
    MEDIUM = "Средний"
    HIGH = "Высокий"

# Базовая модель компании
class CompanyBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)

class Company(CompanyBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    supabase_id: Optional[str] = Field(default=None, index=True)
    is_synced: bool = Field(default=False)
    is_deleted: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    users: List["User"] = Relationship(back_populates="company")
    tasks: List["Task"] = Relationship(back_populates="company")    

# Базовая модель задачи
class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    assignee_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)
    company_id: int = Field(default=None, foreign_key="company.id", index=True)
    due_date: Optional[date] = None
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    status: TaskStatus = Field(default=TaskStatus.TODO)

# Основная модель задачи
class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    supabase_id: Optional[str] = Field(default=None, index=True)
    is_synced: bool = Field(default=False)
    is_deleted: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    history: List["TaskHistory"] = Relationship(back_populates="task")
    assignee: Optional["User"] = Relationship(back_populates="tasks")
    company: Optional["Company"] = Relationship(back_populates="tasks")

# Модель истории изменений задач мб в будущем
class TaskHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: Optional[int] = Field(default=None, foreign_key="task.id", index=True)
    field_name: str # Какое поле изменили
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changed_by: Optional[str] = None
    changed_at: datetime = Field(default_factory=datetime.utcnow)
    task: Optional[Task] = Relationship(back_populates="history")


# Модели связанные с пользователями

# Статус пользователя
class UserStatus(str, Enum):
    MANAGER = "Управляющий"
    EMPLOYEE = "Сотрудник"

# Базовая модель пользователя
class UserBase(SQLModel):
    user_name: str = Field(min_length=1, max_length=255)
    email: EmailStr = Field(min_length=1, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20, regex=r"^\+?[1-9]\d{1,14}$")
    telegram: Optional[str] = Field(default=None, max_length=40, regex=r"^@\w+$")
    company_id: int = Field(default=None, foreign_key="company.id", index=True)
    status: UserStatus = Field(default = UserStatus.EMPLOYEE)

# Основная модель пользователя
class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    supabase_id: Optional[str] = Field(default=None, index=True)
    is_synced: bool = Field(default=False)
    is_deleted: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)  
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    tasks: List["Task"] = Relationship(back_populates="assignee")
    company: Optional["Company"] = Relationship(back_populates="users")

# Модели для API

# Присваивание базовых параметров классу TaskCreate
class TaskCreate(TaskBase):
    pass

# Класс для обновления таблиц с задачами
class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    company_id: Optional[int] = None
    due_date: Optional[date] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None

# Класс для чтения всей инфы о задачах 
class TaskRead(TaskBase):
    id: int
    supabase_id: Optional[str] = None
    is_synced: bool = False
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime
    company_id: int 

# Класс для чтения всей инфы о пользователях
class UserRead(UserBase):
    id: int
    supabase_id: Optional[str] = None
    is_synced: bool = False
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime
    company_id: int 

# Присваивание базовых параметров классу UserCreate
class UserCreate(UserBase):
    pass

# Класс для обновления таблиц с пользователями
class UserUpdate(SQLModel):
    user_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    telegram: Optional[str] = None
    company_id: Optional[int] = None
    status: Optional[UserStatus] = None


class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None

class CompanyRead(CompanyBase):
    id: int
    supabase_id: Optional[str] = None
    is_synced: bool = False
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime


# Модель лога синхронизации
class SyncLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    action: str  # CREATE, UPDATE, DELETE
    table_name: str # Название таблицы
    record_id: int # ID измененной записи
    supabase_id: Optional[str] = None
    sync_timestamp: datetime = Field(default_factory=datetime.utcnow)
