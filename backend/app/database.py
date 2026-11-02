import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Читаем URL из переменной окружения (ее передаст Docker Compose)
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/fridge_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# Dependency для получения сессии базы данных в эндпоинтах
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()