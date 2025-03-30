from fastapi import FastAPI, APIRouter

from src.api import auth_router, users_router, files_router


def apply_routers(app: FastAPI) -> FastAPI:
    main_router = APIRouter(prefix="/api")

    main_router.include_router(auth_router)
    main_router.include_router(users_router)
    main_router.include_router(files_router)

    app.include_router(main_router)

    return app
