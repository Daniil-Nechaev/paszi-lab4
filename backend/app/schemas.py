from pydantic import BaseModel, Field, field_validator
import re

class UserCreate(BaseModel):
    login: str = Field(..., min_length=3, max_length=32)
    password: str = Field(..., min_length=8)

    @field_validator('password')
    @classmethod
    def password_must_be_strong(cls, v: str) -> str:
        if not re.search(r'[A-Z]', v):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        if not re.search(r'[a-z]', v):
            raise ValueError('Пароль должен содержать хотя бы одну строчную букву')
        if not re.search(r'\d', v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        if not re.search(r'[^A-Za-z0-9]', v):
            raise ValueError('Пароль должен содержать хотя бы один специальный символ')
        return v

class ResourceCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="")
    expires_at: str = Field(default="")

class ResourceUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    expires_at: str | None = None

class PermissionUpdate(BaseModel):
    target_user_id: int
    can_read: bool = False
    can_update: bool = False
    can_delete: bool = False
