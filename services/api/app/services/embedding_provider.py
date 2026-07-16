from collections.abc import Sequence
from typing import Any

import httpx

from app.core.config import Settings, settings
from app.core.errors import (
    AppError,
    embedding_not_configured,
    embedding_provider_error,
)

_EMBEDDING_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings"
_EMBEDDING_MODEL = "text-embedding-v4"
_EMBEDDING_DIMENSIONS = 1024
_REQUEST_TIMEOUT_SECONDS = 15.0


class DashScopeEmbeddingProvider:
    def __init__(
        self,
        *,
        settings: Settings = settings,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._api_key = settings.dashscope_api_key
        self._transport = transport

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        if not self._api_key:
            raise embedding_not_configured()

        try:
            with httpx.Client(
                transport=self._transport,
                timeout=_REQUEST_TIMEOUT_SECONDS,
            ) as client:
                response = client.post(
                    _EMBEDDING_URL,
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    json={
                        "model": _EMBEDDING_MODEL,
                        "input": list(texts),
                        "dimensions": _EMBEDDING_DIMENSIONS,
                    },
                )
                response.raise_for_status()
                data: list[dict[str, Any]] = response.json()["data"]
                return [item["embedding"] for item in data]
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as error:
            if isinstance(error, AppError):
                raise
            raise embedding_provider_error() from error
