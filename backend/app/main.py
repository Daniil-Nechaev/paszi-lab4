import logging
from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from app.database import engine, Base, get_db
from app.models import User, Resource, ResourcePermission
from app.schemas import UserCreate, ResourceCreate, ResourceUpdate, PermissionUpdate
from app.core.security import get_password_hash, verify_password
from app import models

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Obshchaga Fridge DAC API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/register", status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.login == user_in.login).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Логин уже занят")
    password_hash = get_password_hash(user_in.password)
    new_user = User(login=user_in.login, password_hash=password_hash)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "login": new_user.login}

@app.post("/api/login")
def login_user(user_in: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.login == user_in.login).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    if not verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный пароль")
    return {"id": user.id, "login": user.login}

def get_current_user_id(x_user_id: int = Header(..., description="ID текущего пользователя")) -> int:
    return x_user_id

@app.post("/api/resources", status_code=status.HTTP_201_CREATED)
def create_resource(res_in: ResourceCreate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    new_resource = Resource(title=res_in.title, description=res_in.description, expires_at=res_in.expires_at, owner_id=user_id)
    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)
    return {"id": new_resource.id, "title": new_resource.title, "description": new_resource.description, "expires_at": new_resource.expires_at, "owner_id": new_resource.owner_id}

@app.get("/api/resources")
def get_resources(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    owned = db.query(Resource).filter(Resource.owner_id == user_id).all()
    permitted_subquery = db.query(ResourcePermission.resource_id).filter(
        ResourcePermission.user_id == user_id, ResourcePermission.can_read == True
    ).subquery()
    shared = db.query(Resource).filter(Resource.id.in_(permitted_subquery)).all()
    all_visible = {r.id: r for r in owned + shared}
    
    result = []
    for r in all_visible.values():
        is_owner = r.owner_id == user_id
        perm = None
        if not is_owner:
            perm = db.query(ResourcePermission).filter(
                ResourcePermission.resource_id == r.id,
                ResourcePermission.user_id == user_id
            ).first()
        result.append({
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "expires_at": r.expires_at,
            "owner_id": r.owner_id,
            "is_owner": is_owner,
            "can_update": is_owner or (perm.can_update if perm else False),
            "can_delete": is_owner or (perm.can_delete if perm else False),
        })
    return result

@app.get("/api/resources/{resource_id}")
def get_resource_detail(resource_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    if resource.owner_id != user_id:
        perm = db.query(ResourcePermission).filter(ResourcePermission.resource_id == resource_id, ResourcePermission.user_id == user_id).first()
        if not perm or not perm.can_read:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="🚫 Не трогай, это не твое!")
    return {"id": resource.id, "title": resource.title, "description": resource.description, "expires_at": resource.expires_at, "owner_id": resource.owner_id}

@app.put("/api/resources/{resource_id}")
def update_resource(resource_id: int, res_in: ResourceUpdate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    if resource.owner_id != user_id:
        perm = db.query(ResourcePermission).filter(ResourcePermission.resource_id == resource_id, ResourcePermission.user_id == user_id).first()
        if not perm or not perm.can_update:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="🚫 Руки прочь! Нет права can_update")
    if res_in.title is not None: resource.title = res_in.title
    if res_in.description is not None: resource.description = res_in.description
    if res_in.expires_at is not None: resource.expires_at = res_in.expires_at
    db.commit()
    return {"message": "Продукт успешно изменён!"}

@app.delete("/api/resources/{resource_id}")
def delete_resource(resource_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    if resource.owner_id != user_id:
        perm = db.query(ResourcePermission).filter(ResourcePermission.resource_id == resource_id, ResourcePermission.user_id == user_id).first()
        if not perm or not perm.can_delete:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="🚫 Нельзя удалять чужую еду без права can_delete!")
    db.delete(resource)
    db.commit()
    return {"message": "Продукт удалён!"}

@app.post("/api/resources/{resource_id}/permissions")
def set_permissions(resource_id: int, perm_in: PermissionUpdate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    if resource.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только владелец может раздавать права!")
    permission = db.query(ResourcePermission).filter(ResourcePermission.resource_id == resource_id, ResourcePermission.user_id == perm_in.target_user_id).first()
    if not permission:
        permission = ResourcePermission(resource_id=resource_id, user_id=perm_in.target_user_id, can_read=perm_in.can_read, can_update=perm_in.can_update, can_delete=perm_in.can_delete)
        db.add(permission)
    else:
        permission.can_read = perm_in.can_read
        permission.can_update = perm_in.can_update
        permission.can_delete = perm_in.can_delete
    db.commit()
    return {"message": "Права успешно обновлены"}
