import re
from pydantic import BaseModel, Field, field_validator

class UserCreate(BaseModel):
    login: str = Field(..., min_length=3, max_length=32)
    password: str = Field(..., min_length=8)

    @field_validator("login")
    @classmethod
    def validate_login(cls, v: str) -> str:
        if not re.match(f"^[a-zA-Z0-9._-]+$", v):
            raise ValueError(
                "Логин должен содержать только латинские буквы, цифры, точку, дефис и нижнее подчеркивание"
            )
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
        if not re.search(r"[a-z]", v):
            raise ValueError("Пароль должен содержать хотя бы одну строчную букву")
        if not re.search(r"\d", v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", v):
            raise ValueError("Пароль должен содержать хотя бы один специальный символ")
        return v

class UserResponse(BaseModel):
    id: int
    login: str

    class Config:
        from_attributes = True

class ResourceCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)  # Например, "Пицца Пепперони"
    description: str = Field(default="")                     # Описание / статус (например, "8 кусков")
    expires_at: str = Field(default="Свежее (до конца недели)") # Срок годности

class ResourceUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    expires_at: str | None = None

class PermissionUpdate(BaseModel):
    target_user_id: int
    can_read: bool = False    # Изучить этикетку / проверить срок годности (Read)
    can_update: bool = False  # Откусить / переставить / подсыпать снотворное (Update)
    can_delete: bool = False  # Схомячить полностью / выбросить просрочку (Delete)