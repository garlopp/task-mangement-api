from sqlalchemy.orm import Session
from models import TaskModel, SharedTaskTokenModel
from schemas import TaskCreate, TaskUpdate
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets


def create_task(db: Session, task: TaskCreate, user_id: int):
    db_task = TaskModel(**task.dict(), owner_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks(db: Session, user_id: int):
    return db.query(TaskModel).filter(TaskModel.owner_id == user_id).all()

def get_task(db: Session, task_id: int, user_id: int):
    return db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.owner_id == user_id).first()

def update_task(db: Session, task_id: int, user_id: int, task: TaskUpdate):
    db_task = get_task(db, task_id, user_id)
    if not db_task:
        return None
    for key, value in task.dict(exclude_unset=True).items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int, user_id: int):
    db_task = get_task(db, task_id, user_id)
    if not db_task:
        return None
    db.delete(db_task)
    db.commit()
    return db_task

def create_shared_task_token(db: Session, task_id: int, email_to_share_with: str, expires_delta_days: int = 7) -> SharedTaskTokenModel:
    """
    Creates a new share token for a task.
    """
    token_value = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=expires_delta_days)
    
    db_shared_token = SharedTaskTokenModel(
        token=token_value,
        task_id=task_id,
        shared_with_email=email_to_share_with,
        expires_at=expires_at
    )
    db.add(db_shared_token)
    db.commit()
    db.refresh(db_shared_token)
    return db_shared_token

def get_valid_shared_task_token(db: Session, token: str) -> SharedTaskTokenModel | None:
    """
    Retrieves a shared task token if it's valid (exists, active, not expired).
    """
    shared_token = db.query(SharedTaskTokenModel).filter(SharedTaskTokenModel.token == token).first()
    if shared_token and shared_token.is_active and shared_token.expires_at and shared_token.expires_at > datetime.utcnow():
        return shared_token
    return None
