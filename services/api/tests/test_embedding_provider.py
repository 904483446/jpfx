import json

import httpx
import pytest
from app.core.config import Settings
from app.core.errors import AppError
from app.services.embedding_provider import DashScopeEmbeddingProvider


def test_embed_sends_text_embedding_v4_request_and_returns_vectors():
    captured_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(
            200,
            json={
                "data": [
                    {"embedding": [0.1, 0.2], "index": 0},
                    {"embedding": [0.3, 0.4], "index": 1},
                ]
            },
        )

    provider = DashScopeEmbeddingProvider(
        settings=Settings(_env_file=None, dashscope_api_key="test-key"),
        transport=httpx.MockTransport(handler),
    )

    assert provider.embed(["第一段", "第二段"]) == [[0.1, 0.2], [0.3, 0.4]]
    assert captured_request is not None
    assert (
        captured_request.url
        == "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings"
    )
    assert captured_request.headers["Authorization"] == "Bearer test-key"
    assert json.loads(captured_request.content) == {
        "model": "text-embedding-v4",
        "input": ["第一段", "第二段"],
        "dimensions": 1024,
    }


def test_embed_rejects_missing_dashscope_key_without_making_request():
    provider = DashScopeEmbeddingProvider(settings=Settings(_env_file=None))

    with pytest.raises(AppError) as captured:
        provider.embed(["正文"])

    assert captured.value.code == "EMBEDDING_NOT_CONFIGURED"
    assert captured.value.message == "未配置 DashScope API Key，无法生成文档向量"


def test_embed_converts_dashscope_failure_to_chinese_app_error():
    provider = DashScopeEmbeddingProvider(
        settings=Settings(_env_file=None, dashscope_api_key="test-key"),
        transport=httpx.MockTransport(
            lambda request: httpx.Response(429, json={"message": "rate limited"})
        ),
    )

    with pytest.raises(AppError) as captured:
        provider.embed(["正文"])

    assert captured.value.code == "EMBEDDING_PROVIDER_ERROR"
    assert captured.value.status_code == 502
    assert captured.value.message == "文档向量生成服务暂时不可用"
