from passlib.context import CryptContext

# Настройка Argon2id с параметрами из требований лабораторной
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,  # 64 MB
    argon2__time_cost=3,        # 3 итерации
    argon2__parallelism=4       # 4 потока
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка соответствия пароля хэшу"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Генерация хэша пароля через Argon2id"""
    return pwd_context.hash(password)