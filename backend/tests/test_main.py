import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Используем SQLite в памяти для быстрых и изолированных тестов
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)


# --- ТЕСТЫ РЕГИСТРАЦИИ (Минимум 3 теста) ---

def test_register_success():
    """Успешная регистрация пользователя"""
    response = client.post(
        "/api/register",
        json={"login": "student1", "password": "StrongPassword1!"}
    )
    assert response.status_code == 201
    assert response.json()["login"] == "student1"
    assert "id" in response.json()


def test_register_duplicate_login():
    """Попытка регистрации с уже занятым логином (ошибка 409)"""
    client.post("/api/register", json={"login": "student1", "password": "StrongPassword1!"})
    
    response = client.post(
        "/api/register",
        json={"login": "student1", "password": "AnotherPassword2@"}
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Логин уже занят"


def test_register_weak_password():
    """Регистрация со слабым паролем (ошибка валидации 422)[cite: 6]"""
    response = client.post(
        "/api/register",
        json={"login": "student2", "password": "123"}
    )
    assert response.status_code == 422


# --- ТЕСТЫ ДИСКРЕЦИОННОЙ МОДЕЛИ ДОСТУПА (DAC) (Минимум 2 теста) ---

def test_dac_allowed_access():
    """Владелец имеет доступ к своему продукту, а сосед получает его по выданным правам"""
    # Регистрируем двух пользователей (ID 1 и ID 2)
    client.post("/api/register", json={"login": "owner_user", "password": "Password1!"})
    client.post("/api/register", json={"login": "neighbor_user", "password": "Password1!"})

    # Владелец (ID: 1) кладет продукт в холодильник
    res = client.post(
        "/api/resources",
        headers={"X-User-Id": "1"},
        json={"title": "Пицца", "description": "8 кусков", "expires_at": "Завтра"}
    )
    assert res.status_code == 201
    resource_id = res.json()["id"]

    # Сосед (ID: 2) пытается прочитать чужой продукт без прав -> получает 403[cite: 6]
    fail_res = client.get(f"/api/resources/{resource_id}", headers={"X-User-Id": "2"})
    assert fail_res.status_code == 403

    # Владелец (ID: 1) выдает соседу право чтения (can_read=True)
    perm_res = client.post(
        f"/api/resources/{resource_id}/permissions",
        headers={"X-User-Id": "1"},
        json={"target_user_id": 2, "can_read": True, "can_update": False, "can_delete": False}
    )
    assert perm_res.status_code == 200

    # Теперь сосед (ID: 2) успешно читает продукт (Разрешенный доступ)[cite: 6]
    success_res = client.get(f"/api/resources/{resource_id}", headers={"X-User-Id": "2"})
    assert success_res.status_code == 200
    assert success_res.json()["title"] == "Пицца"


def test_dac_denied_delete_access():
    """Сосед без права удаления получает отказ (403) при попытке съесть чужой продукт"""
    client.post("/api/register", json={"login": "owner_user", "password": "Password1!"})
    client.post("/api/register", json={"login": "neighbor_user", "password": "Password1!"})

    res = client.post(
        "/api/resources",
        headers={"X-User-Id": "1"},
        json={"title": "Торт", "description": "Целый", "expires_at": "Сегодня"}
    )
    resource_id = res.json()["id"]

    # Сосед (ID: 2) пытается удалить (съесть) продукт без прав удаления
    delete_res = client.delete(f"/api/resources/{resource_id}", headers={"X-User-Id": "2"})
    
    # Ожидаем отказ (403 Forbidden)[cite: 6]
    assert delete_res.status_code == 403
    assert "Нельзя удалять чужую еду" in delete_res.json()["detail"]