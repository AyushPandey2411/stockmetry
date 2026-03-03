"""app/models/user.py"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from ..core.database import Base
import enum


class UserRole(str, enum.Enum):
    admin   = "admin"
    manager = "manager"
    analyst = "analyst"


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    email           = Column(String(255), unique=True, index=True, nullable=False)
    username        = Column(String(100), unique=True, index=True, nullable=False)
    full_name       = Column(String(255), default="")
    hashed_password = Column(String(255), nullable=False)
    role            = Column(String(20), default="analyst", nullable=False)
    is_active       = Column(Boolean, default=True, nullable=False)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    last_login      = Column(DateTime(timezone=True), nullable=True)
    avatar_color    = Column(String(7), default="#6366f1")  # Hex colour for avatar
