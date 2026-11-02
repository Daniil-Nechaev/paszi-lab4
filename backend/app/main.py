import logging
from fastapi import FastAPI, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from app.database import engine, Base, get_db
from app.models import User, Resource, ResourcePermission
from app.schemas import UserCreate, ResourceCreate, ResourceUpdate, PermissionUpdate
from app.core.security import get_password_hash
from app import models

# Настройка структурированного логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаем таблицы в БД при старте приложения (если их еще нет)
    Base.metadata.create_all(bind=engine)
    yield
    # Здесь можно прописать действия при выключении, если понадобятся

app = FastAPI(title="Obshchaga Fridge DAC API", version="1.0.0", lifespan=lifespan)

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


# --- ДИСКРЕЦИОННАЯ МОДЕЛЬ ДОСТУПА (ХОЛОДИЛЬНИК) ---

# Вспомогательная функция для простой имитации авторизации по заголовку X-User-Id
def get_current_user_id(x_user_id: int = Header(..., description="ID текущего пользователя для тестов/UI")) -> int:
    return x_user_id


@app.post("/api/resources", status_code=status.HTTP_201_CREATED)
def create_resource(
    res_in: ResourceCreate, 
    user_id: int = Depends(get_current_user_id), 
    db: Session = Depends(get_db)
):
    """Владелец кладет продукт на полку холодильника"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    new_resource = Resource(
        title=res_in.title,
        description=res_in.description,
        owner_id=user.id
    )
    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)

    logger.info(f"Пользователь {user.id} добавил продукт '{new_resource.title}' в холодильник")
    return {"id": new_resource.id, "title": new_resource.title, "expires_at": new_resource.expires_at, "owner_id": new_resource.owner_id}


@app.get("/api/resources")
def get_resources(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Посмотреть содержимое холодильника (доступное пользователю как владельцу или по правам чтения)"""
    # Пользователь видит свои продукты или те, на которые у него есть право can_read = True
    owned = db.query(Resource).filter(Resource.owner_id == user_id).all()
    
    permitted_subquery = db.query(ResourcePermission.resource_id).filter(
        ResourcePermission.user_id == user_id,
        ResourcePermission.can_read == True
    ).subquery()
    
    shared = db.query(Resource).filter(Resource.id.in_(permitted_subquery)).all()
    
    all_visible = {r.id: r for r in owned + shared}
    
    return [
        {
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "expires_at": r.expires_at,
            "owner_id": r.owner_id,
            "is_owner": r.owner_id == user_id
        }
        for r in all_visible.values()
    ]


@app.get("/api/resources/{resource_id}")
def get_resource_detail(
    resource_id: int, 
    user_id: int = Depends(get_current_user_id), 
    db: Session = Depends(get_db)
):
    """Изучить продукт / проверить срок годности (can_read)"""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Продукт не найден в холодильнике")

    # Проверка доступа: владелец имеет полный доступ, остальные проверяют can_read
    if resource.owner_id != user_id:
        perm = db.query(ResourcePermission).filter(
            ResourcePermission.resource_id == resource_id,
            ResourcePermission.user_id == user_id
        ).first()
        
        if not perm or not perm.can_read:
            logger.warning(f"Пользователь {user_id} попытался прочитать чужой продукт {resource_id} без прав")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="🚫 Не трогай, это не твое! Владелец не дал право даже посмотреть на продукт."
            )

    return {"id": resource.id, "title": resource.title, "description": resource.description, "expires_at": resource.expires_at, "owner_id": resource.owner_id}


@app.put("/api/resources/{resource_id}")
def update_resource(
    resource_id: int,
    res_in: ResourceUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Откусить кусочек / переставить / подсыпать снотворное (can_update)"""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Продукт не найден")

    if resource.owner_id != user_id:
        perm = db.query(ResourcePermission).filter(
            ResourcePermission.resource_id == resource_id,
            ResourcePermission.user_id == user_id
        ).first()
        
        if not perm or not perm.can_update:
            logger.warning(f"Пользователь {user_id} попытался изменить продукт {resource_id} без прав")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="🚫 Руки прочь! Нельзя модифицировать чужую еду без разрешения."
            )

    if res_in.title is not None:
        resource.title = res_in.title
    if res_in.description is not None:
        resource.description = res_in.description
    if res_in.expires_at is not None:
        resource.expires_at = res_in.expires_at

    db.commit()
    logger.info(f"Продукт {resource_id} успешно изменен пользователем {user_id}")
    return {"message": "Состояние продукта успешно изменено!"}


@app.delete("/api/resources/{resource_id}")
def delete_resource(
    resource_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Схомячить полностью / выбросить просрочку (can_delete)"""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Продукт уже пропал или съеден")

    if resource.owner_id != user_id:
        perm = db.query(ResourcePermission).filter(
            ResourcePermission.resource_id == resource_id,
            ResourcePermission.user_id == user_id
        ).first()
        
        if not perm or not perm.can_delete:
            logger.warning(f"Пользователь {user_id} попытался удалить продукт {resource_id} без прав")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="🚫 Нельзя доедать или выбрасывать чужую еду без права на удаление!"
            )

    db.delete(resource)
    db.commit()
    logger.info(f"Продукт {resource_id} ликвидирован пользователем {user_id}")
    return {"message": "Продукт полностью съеден или утилизирован!"}


@app.post("/api/resources/{resource_id}/permissions")
def set_permissions(
    resource_id: int,
    perm_in: PermissionUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Владелец выдает права другим пользователям"""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Продукт не найден")

    # Только владелец может управлять правами своего ресурса в дискреционной модели!
    if resource.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только владелец продукта может раздавать права на него!"
        )

    # Ищем существующую запись прав для этого пользователя на этот ресурс
    permission = db.query(ResourcePermission).filter(
        ResourcePermission.resource_id == resource_id,
        ResourcePermission.user_id == perm_in.target_user_id
    ).first()

    if not permission:
        permission = ResourcePermission(
            resource_id=resource_id,
            user_id=perm_in.target_user_id,
            can_read=perm_in.can_read,
            can_update=perm_in.can_update,
            can_delete=perm_in.can_delete
        )
        db.add(permission)
    else:
        permission.can_read = perm_in.can_read
        permission.can_update = perm_in.can_update
        permission.can_delete = perm_in.can_delete

    db.commit()
    logger.info(f"Владелец {user_id} обновил права для пользователя {perm_in.target_user_id} на продукт {resource_id}")
    return {"message": "Права успешно обновлены"}