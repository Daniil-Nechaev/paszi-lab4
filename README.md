# 🧊 Общажный холодильник (DAC API) — Лабораторная работа №4

**Дисциплина:** «Программно-аппаратные средства защиты информации»
**Тема:** Регистрация пользователя и модели разграничения доступа
**Вариант:** 2 (Дискреционная модель доступа — DAC)

**Выполнили:**
*   Нечаев Даниил, студент группы N3345
*   Щигельская Александра, студентка группы N3348

---

## 📖 Описание проекта

Веб-приложение «Холодильник в общаге» — это минимальная система для управления общими ресурсами (продуктами) с безопасной регистрацией пользователей (хэширование паролей алгоритмом Argon2id) и реализацией **дискреционной модели разграничения доступа (DAC)** на стороне бэкенда.

Каждый продукт (ресурс) имеет владельца. Владелец может выдавать права на чтение (`can_read`), изменение (`can_update`) и удаление (`can_delete`) другим пользователям. Без явно выданного права доступ запрещается (возвращается ошибка `403 Forbidden`).

---

## 🚀 Стек технологий
*   **Frontend:** React, TypeScript, Vite
*   **Backend:** Python 3.11, FastAPI
*   **База данных:** PostgreSQL 15
*   **ORM и миграции:** SQLAlchemy, Alembic
*   **Контейнеризация:** Docker, Docker Compose

---

## 📂 Структура проекта

```text
.
├── backend/
│   ├── alembic/
│   │   ├── versions/
│   │   │   └── 0001_initial.py  # Миграция создания таблиц
│   │   └── env.py               # Настройки миграций
│   ├── app/
│   │   ├── core/                # Модуль безопасности (Argon2id)
│   │   ├── __init__.py
│   │   ├── config.py            # Настройки (pydantic-settings)
│   │   ├── database.py          # Подключение к БД (SQLAlchemy)
│   │   ├── main.py              # Основные эндпоинты FastAPI
│   │   ├── models.py            # Модели SQLAlchemy
│   │   └── schemas.py           # Схемы валидации Pydantic
│   ├── tests/
│   │   └── test_main.py         # Автотесты (pytest)
│   ├── .env                     # Локальные секреты (в gitignore)
│   ├── alembic.ini              # Конфигурация Alembic
│   ├── Dockerfile               # Dockerfile для бэкенда
│   └── requirements.txt         # Зависимости Python
├── frontend/
│   ├── public/
│   │   ├── favicon.svg
│   │   └── icons.svg
│   ├── src/
│   │   ├── api/
│   │   │   └── api.ts           # Настройка axios и запросы к API
│   │   ├── assets/              # Статические ресурсы (картинки, svg)
│   │   ├── pages/
│   │   │   ├── AuthPage.tsx     # Страница входа/регистрации
│   │   │   └── FridgePage.tsx   # Главная страница холодильника
│   │   ├── App.css
│   │   ├── App.tsx              # Корневой компонент и роутинг
│   │   ├── index.css
│   │   └── main.tsx             # Точка входа React
│   ├── .dockerignore
│   ├── .gitignore
│   ├── Dockerfile               # Dockerfile для фронтенда
│   ├── eslint.config.js
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── tsconfig.app.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   └── vite.config.ts
├── .env.example                 # Пример переменных окружения
├── .gitignore
├── docker-compose.yml           # Конфигурация Docker Compose
└── README.md
```

---

## 🛠️ Инструкция запуска (через Docker Compose)

Проект полностью контейнеризирован. Для запуска всей инфраструктуры (База данных, Backend, Frontend) требуется только установленный Docker Desktop.

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/Daniil-Nechaev/paszi-lab4/tree/main 
   cd paszi-lab4
   ```
2. Запустите проект одной командой из корневой папки:
   ```bash
   docker compose up --build
   ```
3. После успешной сборки сервисы будут доступны:
   *   **Frontend (UI):** [http://localhost:5173](http://localhost:5173)
   *   **Backend (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
   *   **PostgreSQL:** `localhost:5432`

*Для остановки проекта нажмите `Ctrl+C` и выполните `docker compose down`.*

---

## 🔐 Модель доступа (Вариант 2 — DAC)

В приложении реализована **Дискреционная модель доступа (DAC)**.
*   У каждого продукта (`Resource`) есть владелец (`owner_id`).
*   Владелец имеет полный доступ к своему ресурсу.
*   Владелец может выдавать права другим пользователям через таблицу `resource_permissions`, устанавливая флаги:
    *   `can_read` (право просмотра)
    *   `can_update` (право изменения)
    *   `can_delete` (право удаления)
*   Проверка прав выполняется исключительно на backend. При отсутствии прав возвращается ошибка `403 Forbidden`.

*(Идентификация пользователя осуществляется передачей его ID в HTTP-заголовке `x_user_id`).*

---

## 🛡️ Безопасность: что сделано

1. **Хэширование паролей:** Пароли не хранятся в открытом виде. Используется стойкий алгоритм **Argon2id** с автоматической генерацией соли.
2. **Валидация:** Строгая проверка логина (от 3 до 32 символов, разрешены латиница, цифры, `.`, `_`, `-`) и пароля (от 8 символов, заглавные, строчные, цифры, спецсимволы). При ошибках возвращается `422`.
3. **Защита от дублирования:** Поле `login` имеет уникальный индекс в БД, при попытке дублирования возвращается `409 Conflict`.
4. **Логирование:** Настроено структурированное логирование. События успеха пишутся в `INFO`, попытки несанкционированного доступа — в `WARNING`. Сырые пароли в логи не попадают.
5. **Ограничения на сервере:** Все проверки прав (DAC) выполняются на бэкенде.

---

## 📡 Описание API и curl-примеры

Все защищенные эндпоинты требуют передачи идентификатора текущего пользователя в HTTP-заголовке `x_user_id`.

### 1. Регистрация пользователя
*   **Метод:** `POST /api/register`
*   **Описание:** Создает нового пользователя. Пароль валидируется и сохраняется в виде хэша (Argon2id).
*   **Тело запроса (JSON):** `{"login": "student1", "password": "StrongPassword1!"}`
*   **Ответ (201 Created):** `{"id": 1, "login": "student1"}`
*   **Ошибки:** `409 Conflict` (логин занят), `422 Unprocessable Entity` (не прошел валидацию).
```bash
curl -X POST http://localhost:8000/api/register \
-H "Content-Type: application/json" \
-d '{"login": "student1", "password": "StrongPassword1!"}'
```

### 2. Вход в систему
*   **Метод:** `POST /api/login`
*   **Описание:** Проверяет логин и пароль, возвращает ID пользователя для дальнейшей работы.
*   **Тело запроса (JSON):** `{"login": "student1", "password": "StrongPassword1!"}`
*   **Ответ (200 OK):** `{"id": 1, "login": "student1"}`
*   **Ошибки:** `404 Not Found` (пользователь не найден), `401 Unauthorized` (неверный пароль).
```bash
curl -X POST http://localhost:8000/api/login \
-H "Content-Type: application/json" \
-d '{"login": "student1", "password": "StrongPassword1!"}'
```

### 3. Создание ресурса (продукта)
*   **Метод:** `POST /api/resources`
*   **Описание:** Создает новый продукт. Текущий пользователь (из заголовка) становится владельцем.
*   **Заголовки:** `x_user_id: 1`
*   **Тело запроса (JSON):** `{"title": "Пицца", "description": "8 кусков", "expires_at": "Завтра"}`
*   **Ответ (201 Created):** Объект созданного ресурса.
```bash
curl -X POST http://localhost:8000/api/resources \
-H "Content-Type: application/json" \
-H "x_user_id: 1" \
-d '{"title": "Пицца", "description": "8 кусков", "expires_at": "Завтра"}'
```

### 4. Просмотр доступных ресурсов
*   **Метод:** `GET /api/resources`
*   **Описание:** Возвращает список продуктов. Пользователь видит свои продукты, а также те, на которые ему выдали право `can_read`.
*   **Заголовки:** `x_user_id: 2`
*   **Ответ (200 OK):** Массив объектов ресурсов.
```bash
curl -X GET http://localhost:8000/api/resources \
-H "x_user_id: 2"
```

### 5. Выдача прав (DAC)
*   **Метод:** `POST /api/resources/{resource_id}/permissions`
*   **Описание:** Позволяет **владельцу** ресурса выдать права другому пользователю.
*   **Заголовки:** `x_user_id: 1` (ID владельца)
*   **Тело запроса (JSON):** `{"target_user_id": 2, "can_read": true, "can_update": false, "can_delete": false}`
*   **Ответ (200 OK):** `{"message": "Права успешно обновлены"}`
*   **Ошибки:** `403 Forbidden` (если запрос делает не владелец).
```bash
curl -X POST http://localhost:8000/api/resources/1/permissions \
-H "Content-Type: application/json" \
-H "x_user_id: 1" \
-d '{"target_user_id": 2, "can_read": true, "can_update": false, "can_delete": false}'
```

### 6. Удаление ресурса
*   **Метод:** `DELETE /api/resources/{resource_id}`
*   **Описание:** Удаляет продукт. Доступно только владельцу или пользователю с флагом `can_delete`.
*   **Заголовки:** `x_user_id: 2` (ID пользователя)
*   **Ответ (200 OK):** `{"message": "Продукт удалён!"}`
*   **Ошибки:** `403 Forbidden` (нет прав на удаление).
```bash
curl -X DELETE http://localhost:8000/api/resources/1 \
-H "x_user_id: 2"
```