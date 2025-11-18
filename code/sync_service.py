import asyncio
from sqlmodel import Session, select
from database import db_manager
from models import Task, User, SyncLog, Company
from datetime import datetime
from sqlalchemy import text

class SimpleSyncService:
    async def start_sync(self):
        """Фоновая синхронизация каждые 60 секунд"""
        while True:
            try:
                if db_manager.is_online:
                    self.sync_data()
                await asyncio.sleep(60)
            except Exception as e:
                print(f"Sync error: {e}")
                await asyncio.sleep(30)
    
    def sync_data(self):
        """Основная логика синхронизации"""
        print("🔄 Starting sync...")
        
        # Синхронизируем в правильном порядке
        self._sync_companies() # Компании
        self._sync_users()    # Пользователи
        self._sync_tasks()    # Задачи
        

        print("✅ Sync completed")
    
    def _sync_companies(self):
        # Синхронизация компаний
        remote_session = db_manager.get_remote_session()
        if not remote_session:
            return

        try:
            with Session(db_manager.local_engine) as local_session:
                # 1. Отправляем локальные компании в Supabase
                local_companies = local_session.exec(select(Company).where(Company.is_synced == False)).all()
                print(f"📤 Syncing {len(local_companies)} companies to Supabase...")

                for company in local_companies:
                    try:
                        # Проверяем, есть ли компания уже в Supabase
                        existing_company = None
                        if company.supabase_id:
                            existing_company = remote_session.exec(select(Company).where(Company.supabase_id == company.supabase_id)).first()
                            
                        if existing_company:
                            # Обновляем существующую компанию
                            existing_company.title = company.title
                            existing_company.description = company.description
                            existing_company.updated_at = datetime.utcnow()
                            remote_company = existing_company

                        else:
                            # Создаем новую компанию в Supabase
                            remote_company = Company(
                                title=company.title,
                                description=company.description,
                                supabase_id=company.supabase_id or f"local_company_{company.id}",
                                created_at=company.created_at,
                                updated_at=company.updated_at
                            )
                            remote_session.add(remote_company)

                        remote_session.commit()
                        remote_session.refresh(remote_company)

                        if not company.supabase_id:
                            company.supabase_id = remote_company.supabase_id
                        
                        company.is_synced = True
                        company.updated_at = datetime.utcnow()
                        local_session.commit()

                        self._log_sync("UPDATE" if existing_company else "CREATE", "company", company.id, company.supabase_id)
                    
                    except Exception as e:
                        print(f"❌ Error syncing company {company.id}: {e}")
                        remote_session.rollback()

                # 2. Получаем компании из Supabase
                remote_companies = remote_session.exec(select(Company)).all()

                print(f"📥 Syncing {len(remote_companies)} companies from Supabase...")

                for remote_company in remote_companies:
                    try:
                        # Проверяем, есть ли компания в локальной БД
                        local_company = local_session.exec(select(Company).where(Company.supabase_id == remote_company.supabase_id)).first()

                        if not local_company:
                            # Добавляем новую компанию в локальную БД
                            new_company = Company(
                                title=remote_company.title,
                                description=remote_company.description,
                                supabase_id=remote_company.supabase_id,
                                is_synced=True,
                                created_at=remote_company.created_at,
                                updated_at=remote_company.updated_at
                            )
                            local_session.add(new_company)
                            local_session.commit()

                            self._log_sync("CREATE", "company", new_company.id, remote_company.supabase_id)
                    
                    except Exception as e:
                        print(f"❌ Error processing remote company {remote_company.id}: {e}")
                        local_session.rollback()

        except Exception as e:
            print(f"❌ Company sync error: {e}")
        finally:
            remote_session.close()


    def _sync_users(self):
        """Синхронизация пользователей"""
        remote_session = db_manager.get_remote_session()
        if not remote_session:
            return
            
        try:
            with Session(db_manager.local_engine) as local_session:
                # 1. Отправляем локальных пользователей в Supabase
                local_users = local_session.exec(
                    select(User).where(User.is_synced == False)).all()
                
                print(f"📤 Syncing {len(local_users)} users to Supabase...")
                
                for user in local_users:
                    try:
                        # Находим соответсвующую компанию в Supabase
                        remote_company_id = None
                        if user.company_id:
                            local_company = local_session.exec(select(Company).where(Company.id == user.company_id)).first()

                            if local_company and local_company.supabase_id:
                                remote_company = remote_session.exec(select(Company).where(Company.supabase_id == local_company.supabase_id)).first()

                                if remote_company:
                                    remote_company_id = remote_company.id
                                else:
                                    print(f"    ⚠️ No remote company found for supabase_id: {local_company.supabase_id}")
                
                        # Проверяем, есть ли пользователь уже в Supabase
                        existing_user = None
                        if user.supabase_id:
                            existing_user = remote_session.exec(select(User).where(User.supabase_id == user.supabase_id)).first()
                        
                        if existing_user:
                            # Обновляем существующего пользователя
                            existing_user.user_name = user.user_name
                            existing_user.email = user.email
                            existing_user.phone = user.phone
                            existing_user.telegram = user.telegram
                            existing_user.status = user.status
                            existing_user.company_id = remote_company_id
                            existing_user.updated_at = datetime.utcnow()
                            remote_user= existing_user
                        else:
                            # Создаем нового пользователя в Supabase
                            remote_user = User(
                                user_name=user.user_name,
                                email=user.email,
                                phone=user.phone,
                                telegram=user.telegram,
                                status=user.status,
                                company_id=remote_company_id,
                                supabase_id=user.supabase_id or f"local_{user.id}",  # ← СОЗДАЕМ УНИКАЛЬНЫЙ ID
                                created_at=user.created_at,
                                updated_at=user.updated_at
                            )
                            remote_session.add(remote_user)
                        
                        remote_session.commit()
                        remote_session.refresh(remote_user)  # ← ПОЛУЧАЕМ НОВЫЙ ID
                        
                        # СОХРАНЯЕМ СООТВЕТСТВИЕ ID
                        if not user.supabase_id:
                            user.supabase_id = remote_user.supabase_id
                        
                        # Помечаем как синхронизированного
                        user.is_synced = True
                        user.updated_at = datetime.utcnow()
                        local_session.commit()
                        
                        self._log_sync("UPDATE" if existing_user else "CREATE", "user", user.id, user.supabase_id)
                        
                    except Exception as e:
                        print(f"❌ Error syncing user {user.id}: {e}")
                        remote_session.rollback()
                
                # 2. Получаем пользователей из Supabase
                remote_users = remote_session.exec(select(User)).all()
                
                print(f"📥 Syncing {len(remote_users)} users from Supabase...")
                
                for remote_user in remote_users:
                    try:
                        # Находим соответствующую компанию в локальной базе
                        local_company_id = None
                        if remote_user.company_id:
                            remote_company = remote_session.exec(select(Company).where(Company.id == remote_user.company_id)).first()

                            if remote_company and remote_company.supabase_id:
                                local_company = local_session.exec(select(Company).where(Company.supabase_id == remote_company.supabase_id)).first()

                                if local_company:
                                    local_company_id = local_company.id

                        # Проверяем, есть ли пользователь в локальной БД
                        local_user = local_session.exec(
                            select(User).where(User.supabase_id == remote_user.supabase_id)).first()
                        
                        if not local_user:
                            # Добавляем нового пользователя в локальную БД
                            new_user = User(
                                user_name=remote_user.user_name,
                                email=remote_user.email,
                                phone=remote_user.phone,
                                telegram=remote_user.telegram,
                                status=remote_user.status,
                                company_id=local_company_id,
                                supabase_id=remote_user.supabase_id,
                                is_synced=True,
                                created_at=remote_user.created_at,
                                updated_at=remote_user.updated_at
                            )
                            local_session.add(new_user)
                            local_session.commit()
                            
                            self._log_sync("CREATE", "user", new_user.id, remote_user.supabase_id)
                        
                    except Exception as e:
                        print(f"    ❌ Error processing remote user {remote_user.id}: {e}")
    
        except Exception as e:
            print(f"❌ User sync error: {e}")
        finally:
            remote_session.close()
    
    def _sync_tasks(self):
        """Синхронизация задач"""
        remote_session = db_manager.get_remote_session()
        if not remote_session:
            return
            
        try:
            with Session(db_manager.local_engine) as local_session:
                # 1. Получаем непосинхронизированные задачи из локальной БД
                local_tasks = local_session.exec(
                    select(Task).where(Task.is_synced == False)
                ).all()
                
                print(f"📤 Syncing {len(local_tasks)} tasks to Supabase...")
                
                
                for task in local_tasks:
                    try:
                        # НАХОДИМ СООТВЕТСТВУЮЩЕГО ПОЛЬЗОВАТЕЛЯ В SUPABASE
                        remote_assignee_id = None
                        if task.assignee_id:
                            local_user = local_session.exec(select(User).where(User.id == task.assignee_id)).first()
                            
                            if local_user and local_user.supabase_id:
                                remote_user = remote_session.exec(
                                    select(User).where(User.supabase_id == local_user.supabase_id)).first()
                                
                                if remote_user:
                                    remote_assignee_id = remote_user.id
                                else:
                                    print(f"    ⚠️ No remote user found for supabase_id: {local_user.supabase_id}")
                            else:
                                print(f"    ⚠️ Local user {task.assignee_id} not found or has no supabase_id")
                        
                        # Находим соответсвующую компанию в Supabase
                        remote_company_id = None
                        if task.company_id:
                            local_company = local_session.exec(select(Company).where(Company.id == task.company_id)).first()

                            if local_company and local_company.supabase_id:
                                remote_company = remote_session.exec(select(Company).where(Company.supabase_id == local_company.supabase_id)).first()

                                if remote_company:
                                    remote_company_id = remote_company.id
                                else:
                                    print(f"    ⚠️ No remote company found for supabase_id: {local_company.supabase_id}")
                            
                        # Проверяем, есть ли задача уже в Supabase
                        existing_task = None
                        if task.supabase_id:
                            existing_task = remote_session.exec(
                                select(Task).where(Task.supabase_id == task.supabase_id)).first()
                        
                        if existing_task:
                            # Обновляем существующую задачу
                            existing_task.title = task.title
                            existing_task.description = task.description
                            existing_task.assignee_id = remote_assignee_id
                            existing_task.company_id = remote_company_id
                            existing_task.due_date = task.due_date
                            existing_task.priority = task.priority
                            existing_task.status = task.status
                            existing_task.updated_at = datetime.utcnow()
                            remote_task = existing_task
                        else:
                            # Создаем новую задачу в Supabase
                            remote_task = Task(
                                title=task.title,
                                description=task.description,
                                assignee_id=remote_assignee_id,
                                company_id=remote_company_id,
                                due_date=task.due_date,
                                priority=task.priority,
                                status=task.status,
                                supabase_id=task.supabase_id or f"local_task_{task.id}",
                                is_synced=True,
                                is_deleted=task.is_deleted,
                                created_at=task.created_at,
                                updated_at=task.updated_at
                            )
                            remote_session.add(remote_task)
                        
                        remote_session.commit()
                        
                        # Помечаем как синхронизированную
                        task.is_synced = True
                        task.updated_at = datetime.utcnow()
                        local_session.commit()
                        
                        self._log_sync("UPDATE" if existing_task else "CREATE", "task", task.id, task.supabase_id)
                        
                    except Exception as e:
                        print(f"    ❌ Error syncing task {task.id}: {e}")
                        remote_session.rollback()
                
                # 2. Получаем задачи из Supabase для обновления локальной БД
                remote_tasks = remote_session.exec(select(Task)).all()
                
                print(f"📥 Syncing {len(remote_tasks)} tasks from Supabase...")
                
                for remote_task in remote_tasks:
                    try:
                        # Находим соответсвующего пользователя в локальной базе
                        local_assignee_id = None
                        if remote_task.assignee_id:
                            # Получаем пользователя из удаленной базы
                            remote_user = remote_session.exec(
                                select(User).where(User.id == remote_task.assignee_id)).first()
                            
                            if remote_user and remote_user.supabase_id:
                                # Ищем пользователя в локальной базе по supabase_id
                                local_user = local_session.exec(
                                    select(User).where(User.supabase_id == remote_user.supabase_id)).first()
                                
                                if local_user:
                                    local_assignee_id = local_user.id
                        
                        # Находим соответсвующую компанию в локальной базе
                        local_company_id = None
                        if remote_task.company_id:
                            remote_company = remote_session.exec(select(Company).where(Company.id == remote_task.company_id)).first()

                            if remote_company and remote_company.supabase_id:
                                local_company = local_session.exec(select(Company).where(Company.supabase_id == remote_company.supabase_id)).first()

                                if local_company:
                                    local_company_id = local_company.id
                        
                        # Проверяем, есть ли задача в локальной БД
                        local_task = local_session.exec(
                            select(Task).where(Task.supabase_id == remote_task.supabase_id)).first()
                        
                        if not local_task:
                            # Добавляем новую задачу в локальную БД
                            new_task = Task(
                                title=remote_task.title,
                                description=remote_task.description,
                                assignee_id=local_assignee_id,
                                company_id=local_company_id,
                                due_date=remote_task.due_date,
                                priority=remote_task.priority,
                                status=remote_task.status,
                                supabase_id=remote_task.supabase_id,
                                is_synced=True,
                                is_deleted=remote_task.is_deleted,
                                created_at=remote_task.created_at,
                                updated_at=remote_task.updated_at
                            )
                            local_session.add(new_task)
                            local_session.commit()
                            
                            
                            self._log_sync("CREATE", "task", new_task.id, remote_task.supabase_id)
                            
                    except Exception as e:
                        print(f"    ❌ Error processing remote task {remote_task.id}: {e}")
                        
        except Exception as e:
            print(f"❌ Task sync error: {e}")
        finally:
            remote_session.close()
                
    
    
    def _log_sync(self, action: str, table_name: str, record_id: int, supabase_id: str = None):
        """Логирование синхронизации"""
        try:
            with Session(db_manager.local_engine) as session:
                sync_log = SyncLog(
                    action=action,
                    table_name=table_name,
                    record_id=record_id,
                    supabase_id=supabase_id,
                    sync_timestamp=datetime.utcnow()
                )
                session.add(sync_log)
                session.commit()
        except Exception as e:
            print(f"❌ Error logging sync: {e}")

sync_service = SimpleSyncService()