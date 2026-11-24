"""Database and application configuration module.

Reads parameters from .env file with production-ready defaults.
Never exposes credentials in logs or output.
"""

from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()


class DatabaseConfig:
    HOST: str = os.getenv("DB_HOST", "127.0.0.1")
    PORT: int = int(os.getenv("DB_PORT", "3306"))
    NAME: str = os.getenv("DB_NAME", "agricultural_market_db")
    USER: str = os.getenv("DB_USER", "root")
    PASSWORD: str = os.getenv("DB_PASSWORD", "admin")
    POOL_NAME: str = os.getenv("DB_POOL_NAME", "agri_pool")
    POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))

    @classmethod
    def get_connection_dict(cls) -> dict:
        return {
            "host": cls.HOST,
            "port": cls.PORT,
            "user": cls.USER,
            "password": cls.PASSWORD,
            "database": cls.NAME,
            "autocommit": True,
            "charset": "utf8mb4",
        }

    @classmethod
    def get_sqlalchemy_uri(cls) -> str:
        return f"mysql+mysqlconnector://{cls.USER}:{cls.PASSWORD}@{cls.HOST}:{cls.PORT}/{cls.NAME}"


class AppConfig:
    TITLE: str = os.getenv("APP_TITLE", "Agricultural Market Pricing & Sales Dashboard")
    ENV: str = os.getenv("APP_ENV", "production")
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "15"))
    DATA_RAW_DIR: Path = BASE_DIR / "data" / "raw"
    DATA_PROCESSED_DIR: Path = BASE_DIR / "data" / "processed"
    DOCS_DIR: Path = BASE_DIR / "docs"
