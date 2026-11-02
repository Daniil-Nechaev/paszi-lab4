from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Boolean, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    login: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    resources: Mapped[list["Resource"]] = relationship(back_populates="owner")


class Resource(Base):
    """Еда в холодильнике (ресурс)"""
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    expires_at: Mapped[str] = mapped_column(String(100), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    owner: Mapped[User] = relationship(back_populates="resources")
    permissions: Mapped[list["ResourcePermission"]] = relationship("ResourcePermission", back_populates="resource", cascade="all, delete-orphan")


class ResourcePermission(Base):
    """Таблица дискреционного доступа (какие права у соседа на эту еду)"""
    __tablename__ = "resource_permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    can_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_update: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_delete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    resource: Mapped["Resource"] = relationship("Resource", back_populates="permissions")
    user: Mapped["User"] = relationship("User")

    __table_args__ = (UniqueConstraint("resource_id", "user_id", name="uq_resource_user"),)