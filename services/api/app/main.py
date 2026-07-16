from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.auth import router as auth_router
from app.api.v1.documents import documents_router
from app.api.v1.documents import spaces_router as documents_spaces_router
from app.api.v1.health import router as health_router
from app.api.v1.retrieval import router as retrieval_router
from app.api.v1.spaces import router as spaces_router
from app.core.config import settings
from app.core.errors import (
    AppError,
    app_exception_handler,
    http_exception_handler,
    internal_exception_handler,
    validation_exception_handler,
)


def create_app() -> FastAPI:
    application = FastAPI(title=settings.app_name)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type"],
    )
    application.add_exception_handler(
        StarletteHTTPException,
        http_exception_handler,
    )
    application.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )
    application.add_exception_handler(AppError, app_exception_handler)
    application.add_exception_handler(Exception, internal_exception_handler)
    application.include_router(auth_router, prefix=settings.api_v1_prefix)
    application.include_router(health_router, prefix=settings.api_v1_prefix)
    application.include_router(spaces_router, prefix=settings.api_v1_prefix)
    application.include_router(documents_spaces_router, prefix=settings.api_v1_prefix)
    application.include_router(documents_router, prefix=settings.api_v1_prefix)
    application.include_router(retrieval_router, prefix=settings.api_v1_prefix)
    return application


app = create_app()
