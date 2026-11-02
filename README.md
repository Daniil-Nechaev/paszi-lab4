# 🧊 Холодильник в общаге (DAC API)

Лабораторная работа № 4 по ПАСЗИ. Реализует бэкенд с дискреционной моделью доступа (DAC) к ресурсам общего холодильника.

---

## 🚀 Стек технологий
- **Python 3.10+ / FastAPI**
- **PostgreSQL + SQLAlchemy**
- **Pydantic, Passlib (Argon2id)**

---

## 🛠️ Инструкция для фронтендера (Локальный запуск)

Если вы хотите запустить бэкенд локально для разработки и тестирования интерфейса:

1. **Перейдите в папку бэкенда:**
   ``` 
   cd backend
   ```

2. **Создайте и активируйте виртуальное окружение:**
    ```
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # Linux / macOS:
    source venv/bin/activate
    ```

3. **Установите зависимости:**
    ```
    pip install -r requirements.txt

    ```


4. **Создайте файл `.env` в папке `backend/` на основе `.env.example`:**
    ```
    DATABASE_URL=postgresql://postgres:ТВОЙ_ПАРОЛЬ@localhost:5432/fridge_db

    ```


5. **Запустите сервер разработки:**
    ```
    uvicorn app.main:app --reload

    ```


Сервер будет доступен по адресу: `http://127.0.0.1:8000`

---

## 🐳 Запуск через Docker Compose (Альтернатива)

Если у вас установлен Docker, поднять всю инфраструктуру (PostgreSQL + FastAPI бэкенд) вместе можно одной командой из корня проекта:

    docker compose up --build


---

## 📚 Документация и тестирование API

После запуска сервера интерактивная документация доступна в браузере:

* **Swagger UI:** [http://127.0.0.1:8000/docs](https://www.google.com/search?q=http://127.0.0.1:8000/docs)
* **ReDoc:** [http://127.0.0.1:8000/redoc](https://www.google.com/search?q=http://127.0.0.1:8000/redoc)

---

## 🔑 Важное правило для фронтенда (Авторизация и DAC)

Для эндпоинтов, где требуется проверка прав владельца или пользователя (DAC), в запросы необходимо передавать заголовок **`x_user_id`** с ID текущего авторизованного пользователя.

Пример запроса из фронтенда (на JavaScript / `fetch`):

```javascript
const response = await fetch("[http://127.0.0.1:8000/api/resources/1](http://127.0.0.1:8000/api/resources/1)", {
  method: "GET",
  headers: {
    "Content-Type": "application/json",
    "x_user_id": "1" // ID пользователя из базы данных
  }
});
