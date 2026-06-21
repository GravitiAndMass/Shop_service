import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr

load_dotenv()  # Load variables from .env file


class AppConfig:
    """
    Конфигурация Приложения
    """

    class _AppConfig(BaseModel):
        app_name: str
        secret_key: str
        access_token_expire_minutes: int
        otp_secret_key: str
        otp_expire_seconds: int

    config = _AppConfig(
        app_name=os.getenv("APP_NAME"),
        secret_key=os.getenv("SECRET_KEY"),
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")),
        otp_secret_key=os.getenv("OTP_SECRET_KEY"),
        otp_expire_seconds=int(os.getenv("OTP_EXPIRE_SECONDS")), )

    @classmethod
    def get_config(cls) -> _AppConfig:
        """
        Получить конфигурацию приложения.
        """

        return cls.config


class EmailServiceConfig:
    """
    SMTP Конфигурация.
    """

    class _SMTPConfig(BaseModel):
        smtp_server: str
        smtp_port: int
        smtp_username: EmailStr
        smtp_password: str
        use_local_fallback: bool

    config = _SMTPConfig(
        smtp_server=os.getenv("SMTP_SERVER"),
        smtp_port=int(os.getenv("SMTP_PORT")),
        smtp_username=os.getenv("SMTP_USERNAME"),
        smtp_password=os.getenv("SMTP_PASSWORD"),
        use_local_fallback=os.getenv("USE_LOCAL_FALLBACK", "False").lower() == "true"
    )

    @classmethod
    def get_config(cls) -> _SMTPConfig:
        """
        Получить SMTP конфигурацию
        """

        return cls.config


# -------------------------
# --- Настройки бд ---
# -------------------------

# DATABASES = {
#     "drivername": "postgresql",
#     "username": "",
#     "password": "",
#     "host": "localhost",
#     "database": "",
#     "port": 5432
# }
DATABASES = {
    "drivername": "sqlite",
    "database": "fast_store.db"
}

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR = BASE_DIR / "media"


MEDIA_DIR.mkdir(parents=True, exist_ok=True)


MAX_FILE_SIZE = 5
products_list_limit = 12


