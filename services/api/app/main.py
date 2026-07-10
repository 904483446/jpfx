from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.health import router as health_router
from app.core.config import settings
from app.core.errors import (
    http_exception_handler,
    internal_exception_handler,
    validation_exception_handler,
)


def create_app() -> FastAPI:
    application = FastAPI(title=settings.app_name)
    application.add_exception_handler(
        StarletteHTTPException,
        http_exception_handler,
    )
    application.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )
    application.add_exception_handler(Exception, internal_exception_handler)
    application.include_router(health_router, prefix=settings.api_v1_prefix)
    return application


app = create_app()
