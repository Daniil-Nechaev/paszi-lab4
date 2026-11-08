FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей для компиляции и работы с PostgreSQL (psycopg2)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Установка зависимостей Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода бэкенда
COPY . .

EXPOSE 8000

# Команда запуска сервера разработки / продакшна через Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]