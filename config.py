from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Default values are for local development.
    # In production, these will be replaced by environment variables.

    # Security
    SECRET_KEY: str = "blueface2580"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Application URL
    APP_BASE_URL: str = "http://localhost:8000"

    # Database
    DATABASE_URL: str = "postgresql://postgres:blueface2580@localhost:5432/auth_db"

    # Email sending configuration
    SMTP_SERVER: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "your-email@example.com"
    SMTP_PASSWORD: str = "your-email-password"
    EMAIL_FROM: str = "noreply@example.com"

    # This tells Pydantic to load variables from a .env file (for local dev)
    # and from the environment (for production)
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
