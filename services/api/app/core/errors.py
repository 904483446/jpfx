import logging
from typing import Any

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class AppError(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}


def unauthorized() -> AppError:
    return AppError(
        status_code=401,
        code="UNAUTHORIZED",
        message="登录状态无效或已过期",
    )


def space_not_found() -> AppError:
    return AppError(
        status_code=404,
        code="SPACE_NOT_FOUND",
        message="产品空间不存在",
    )


def analysis_task_not_found() -> AppError:
    return AppError(
        status_code=404,
        code="ANALYSIS_TASK_NOT_FOUND",
        message="分析任务不存在",
    )


def invalid_task_state() -> AppError:
    return AppError(
        status_code=409,
        code="INVALID_TASK_STATE",
        message="当前任务状态不支持此操作",
    )


def invalid_competitor_selection() -> AppError:
    return AppError(
        status_code=422,
        code="INVALID_COMPETITOR_SELECTION",
        message="请选择当前任务中的 1 至 3 个候选竞品",
    )


def document_not_found() -> AppError:
    return AppError(status_code=404, code="DOCUMENT_NOT_FOUND", message="文档不存在")


def document_not_indexable() -> AppError:
    return AppError(
        status_code=409,
        code="DOCUMENT_NOT_INDEXABLE",
        message="当前文档状态不支持开始索引",
    )


def document_type_not_supported() -> AppError:
    return AppError(
        status_code=400,
        code="DOCUMENT_TYPE_NOT_SUPPORTED",
        message="仅支持 PDF、DOCX、TXT 和 MD 文档",
    )


def document_too_large() -> AppError:
    return AppError(
        status_code=400,
        code="DOCUMENT_TOO_LARGE",
        message="单个文档不能超过 20MB",
    )


def document_empty() -> AppError:
    return AppError(status_code=400, code="DOCUMENT_EMPTY", message="文档不能为空")


def document_content_not_extractable() -> AppError:
    return AppError(
        status_code=400,
        code="DOCUMENT_CONTENT_NOT_EXTRACTABLE",
        message="文档未提取到可索引的正文",
    )


def embedding_not_configured() -> AppError:
    return AppError(
        status_code=500,
        code="EMBEDDING_NOT_CONFIGURED",
        message="未配置 DashScope API Key，无法生成文档向量",
    )


def embedding_provider_error() -> AppError:
    return AppError(
        status_code=502,
        code="EMBEDDING_PROVIDER_ERROR",
        message="文档向量生成服务暂时不可用",
    )


def model_config_encryption_not_configured() -> AppError:
    return AppError(
        status_code=500,
        code="MODEL_CONFIG_ENCRYPTION_NOT_CONFIGURED",
        message="模型配置密钥加密未配置",
    )


def model_config_decryption_failed() -> AppError:
    return AppError(
        status_code=500,
        code="MODEL_CONFIG_DECRYPTION_FAILED",
        message="模型配置密钥解密失败",
    )


def deepseek_not_configured() -> AppError:
    return AppError(
        status_code=409,
        code="DEEPSEEK_NOT_CONFIGURED",
        message="未配置 DeepSeek API Key",
    )


def deepseek_provider_error() -> AppError:
    return AppError(
        status_code=502,
        code="DEEPSEEK_PROVIDER_ERROR",
        message="DeepSeek 分析服务暂时不可用",
    )


def analysis_pipeline_error() -> AppError:
    return AppError(
        status_code=502,
        code="ANALYSIS_PIPELINE_ERROR",
        message="分析任务执行失败，请稍后重试",
    )


def search_not_configured() -> AppError:
    return AppError(
        status_code=409,
        code="SEARCH_NOT_CONFIGURED",
        message="未配置 Bocha Search API Key",
    )


def search_provider_error() -> AppError:
    return AppError(
        status_code=502,
        code="SEARCH_PROVIDER_ERROR",
        message="公开网页搜索服务暂时不可用",
    )


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


async def app_exception_handler(
    request: Request,
    exc: AppError,
) -> JSONResponse:
    return error_response(
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return error_response(
        status_code=422,
        code="VALIDATION_ERROR",
        message="请求参数校验失败",
        details={"errors": jsonable_encoder(exc.errors())},
    )


async def internal_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.error(
        "Unhandled exception while processing %s",
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return error_response(
        status_code=500,
        code="INTERNAL_SERVER_ERROR",
        message="服务器内部错误",
        details={},
    )
