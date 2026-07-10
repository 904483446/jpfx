from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            }
        },
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    if exc.status_code == 404:
        return error_response(
            status_code=404,
            code="NOT_FOUND",
            message="接口不存在",
            details={"path": request.url.path},
        )

    return error_response(
        status_code=exc.status_code,
        code="HTTP_ERROR",
        message="请求处理失败",
        details={},
    )
