from fastapi import FastAPI

from src.core.config import get_settings, Settings
from src.routers import apply_routers


settings: Settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.fastapi.title,
        description=settings.fastapi.description,
        version=settings.fastapi.version,
        docs_url=settings.fastapi.docs_url,
        redoc_url=settings.fastapi.redoc_url,
    )

    app = apply_routers(app)

    return app
