from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    login: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Связи
    owned_resources: Mapped[list["Resource"]] = relationship("Resource", back_populates="owner", cascade="all, delete-orphan")
    permissions: Mapped[list["ResourcePermission"]] = relationship("ResourcePermission", back_populates="user", cascade="all, delete-orphan")


class Resource(Base):
    """Еда в холодильнике (ресурс)"""
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)  # Например, "Пицца Пепперони"
    description: Mapped[str] = mapped_column(Text, default="")         # Описание / статус (например, "осталось 8 кусков")
    expires_at: Mapped[str] = mapped_column(String(100), default="Свежее") # Срок годности
    
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    owner: Mapped["User"] = relationship("User", back_populates="owned_resources")
    permissions: Mapped[list["ResourcePermission"]] = relationship("ResourcePermission", back_populates="resource", cascade="all, delete-orphan")


class ResourcePermission(Base):
    """Таблица дискреционного доступа (какие права у соседа на эту еду)"""
    __tablename__ = "resource_permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resource_id: Mapped[int] = mapped_column(Integer, ForeignKey("resources.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    
    can_read: Mapped[bool] = mapped_column(Boolean, default=False)   # Право посмотреть / понюхать
    can_update: Mapped[bool] = mapped_column(Boolean, default=False) # Право откусить / изменить
    can_delete: Mapped[bool] = mapped_column(Boolean, default=False) # Право съесть полностью / удалить

    resource: Mapped["Resource"] = relationship("Resource", back_populates="permissions")
    user: Mapped["User"] = relationship("User", back_populates="permissions")