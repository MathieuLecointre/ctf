from typing import List, Union
import re
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Informations de base de l'API
    PROJECT_NAME: str = "CTF Platform API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # Securite & JWT
    JWT_SECRET_KEY: str = "secret-key-change-in-production-ctf-platform-but5"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # Base de donnees PostgreSQL (fournie par AGEA)
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/ctf"

    @property
    def async_database_url(self) -> str:
        """
        Garantit que l'URL utilise le driver asynchrone asyncpg pour SQLAlchemy.
        Si l'URL commence par postgresql://, elle est convertie en postgresql+asyncpg://
        """
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    # Cache & Pub/Sub Redis (fourni par AGEA)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Orchestration Docker (fournie par RES)
    # Compatible socket local unix:///var/run/docker.sock ou distant tcp://<ip>:2376 (Architecture 2 VM)
    DOCKER_HOST: str = "unix://var/run/docker.sock"
    DOCKER_NETWORK_PREFIX: str = "ctf_player"
    TRAEFIK_NETWORK: str = "traefik-net"
    TRAEFIK_DOMAIN: str = "ctf.local"

    # Regles metier & Limites des instances
    INSTANCE_TIMEOUT_SECONDS: int = 1800  # 30 minutes
    INSTANCE_CPU_LIMIT: str = "0.5"       # 50% d'un CPU max
    INSTANCE_MEM_LIMIT: str = "256m"      # 256 Mo de RAM max
    FLAG_REGEX: str = r"^CTF\{[a-zA-Z0-9_\-\+\=\!\@\#\$\%\^\&\*\?]{4,128}\}$"

    # Configuration CORS (Frontend Vue 3 Vite)
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://ctf.local",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
