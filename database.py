from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()


class SafeDatabaseManager:
    def __init__(self):
        self.local_engine = None # Движок для локальной базы
        self.remote_engine = None # Движок для удаленной базы
        self.is_online = False # Есть интернет?
        
    def init_databases(self):
        self.local_engine = create_engine("sqlite:///./task_manager.db", echo=False, connect_args={"check_same_thread": False}) # Создание движка для локальной базы

        self.remote_engine = self._create_safe_remote_engine() # Создание движка для удаленной базы через функцию
        
        SQLModel.metadata.create_all(self.local_engine) # Создание всех таблиц в базу данных\

        if self.is_online:
            print("✅ Подключение к Supabase установлено!")
            self._create_supabase_tables()
        else:
            print("📡 Работаем в оффлайн режиме")
        

    def _create_supabase_tables(self):
        if not self.remote_engine or not self.is_online:
            return
        try:
            print("🔄 Создаем таблицы в Supabase...")
            SQLModel.metadata.create_all(self.remote_engine)
            print("✅ Таблицы созданы в Supabase!")

        except Exception as e:
            print(f"❌ Ошибка создания таблиц в Supabase: {e}")

    
    def _create_safe_remote_engine(self):
        try:
            USER = os.getenv("user")
            PASSWORD = os.getenv("password")
            HOST = os.getenv("host")
            PORT = os.getenv("port")
            DBNAME = os.getenv("dbname")
            DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"

            engine = create_engine(DATABASE_URL, echo=False)

            with Session(engine) as session:
                session.execute(text("SELECT 1"))
                print ("✅ Подключение к Supabase успешно!")

            self.is_online = True
            return engine
        except Exception as e:
            print(f"Supabase connection failed: {e}")
            print("Подключение к Supabase с ошибкой!!!")
            self.is_online = False
            return None
        
    def get_session(self) -> Generator[Session, None, None]:
        with Session(self.local_engine) as session:
            yield session
    
    def get_remote_session(self):
        if self.remote_engine and self.is_online:
            return Session(self.remote_engine)
        return None
        
db_manager = SafeDatabaseManager()

def create_db_and_tables():
    db_manager.init_databases()

def get_db():
    return db_manager.get_session()
