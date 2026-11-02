from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg2://fridge:fridge_pass@db:5432/fridge_db"
    SECRET_KEY: str = "dev_secret_change_me"
    HASH_SCHEME: str = "argon2id"
    APP_ENV: str = "development"
    PORT: int = 8000

    ARGON2_TIME_COST: int = 2
    ARGON2_MEMORY_COST: int = 65536
    ARGON2_PARALLELISM: int = 2

settings = Settings()