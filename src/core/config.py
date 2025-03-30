from functools import cached_property, lru_cache
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi_sso.sso.yandex import YandexSSO


BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent


class DB(BaseModel):
    host: str = "localhost"
    port: int = 5432
    database: str = "yandex_music"
    user: str = "postgres"
    password: str = "postgres"
    provider: str = "postgresql+asyncpg"

    naming_convention: dict[str, str] = {
        "ix": "%(column_0_label)s_idx",
        "uq": "%(table_name)s_%(column_0_name)s_key",
        "ck": "%(table_name)s_%(constraint_name)s_check",
        "fk": "%(table_name)s_%(column_0_name)s_fkey",
        "pk": "%(table_name)s_pkey",
    }

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class Yandex(BaseModel):
    client_id: str = "some_client_id"
    client_secret: str = "some_client_secret"
    redirect_uri: str = "http://localhost:8000/api/auth/callback"

    @cached_property
    def get_yandex_sso(self) -> YandexSSO:
        return YandexSSO(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            allow_insecure_http=True,
        )


class FastApi(BaseModel):
    title: str = "Yandex Self Music App"
    description: str = "Test FastAPI Project"
    version: str = "0.1.0"
    docs_url: str | None = "/docs"
    redoc_url: str | None = "/redoc"


class Dev(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = True


class Auth(BaseModel):
    secret_key: str = "not_a_secret"
    access_token_expire_minutes: int = 15
    refresh_token_expire_minutes: int = 60 * 24 * 7


class Files(BaseModel):
    max_size: int = 1024 * 1024 * 50
    allowed_types: list[str] = [
        "audio/mpeg",
        "audio/wav",
        "audio/ogg",
        "audio/flac",
    ]


class Settings(BaseSettings):
    db: DB = DB()
    yandex: Yandex = Yandex()
    fastapi: FastApi = FastApi()
    dev: Dev = Dev()
    auth: Auth = Auth()
    files: Files = Files()

    admin_emails: list[str] | None = None

    model_config = SettingsConfigDict(
        env_file=f"{BASE_DIR}/.env",
        case_sensitive=False,
        env_nested_delimiter="__",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
