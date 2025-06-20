from sqlalchemy import Integer, Column, String,Boolean,DateTime,ForeignKey
from sqlalchemy.orm import relationship
from db import Base
from datetime import datetime, timedelta
import secrets 
class UserModel(Base):
    __tablename__ = 'user_data'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    otp_code = Column(String, nullable=True)
    otp_expiry = Column(DateTime, nullable=True)      

class TaskModel(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    due_date = Column(DateTime)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("user_data.id"))
    owner = relationship("UserModel")
    # Relationship to shared tokens (optional, but can be useful)
    shared_tokens = relationship("SharedTaskTokenModel", back_populates="task")
 
class SharedTaskTokenModel(Base):
    __tablename__ = 'shared_task_token'
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False, default=lambda: secrets.token_urlsafe(32))
    task_id = Column(Integer, ForeignKey("task.id"), nullable=False)
    shared_with_email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=7)) # Token expires in 7 days
    is_active = Column(Boolean, default=True) # Can be set to False after use or if revoked

    task = relationship("TaskModel", back_populates="shared_tokens")
