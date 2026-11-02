import logging
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.models import User
from app.schemas import UserCreate
from app.core.security import get_password_hash

# Настройка структурированного логирования (требование лабораторной)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Создание таблиц (для удобства разработки)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Obshchaga Fridge API", version="1.0.0")

@app.post("/api/register", status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    # Проверка, занят ли логин
    existing_user = db.query(User).filter(User.login == user_in.login).first()
    if existing_user:
        logger.warning(f"Попытка регистрации с уже занятым логином: {user_in.login}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Логин уже занят"
        )

    # Хэшируем пароль (СЫРОЙ ПАРОЛЬ НИКОГДА НЕ ЛОГИРУЕТСЯ!)
    password_hash = get_password_hash(user_in.password)

    new_user = User(
        login=user_in.login,
        password_hash=password_hash
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"Успешная регистрация пользователя: {new_user.login} (ID: {new_user.id})")
    return {"message": "user создан"}