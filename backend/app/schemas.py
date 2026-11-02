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