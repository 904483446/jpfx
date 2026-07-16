import json

import httpx
import pytest
from app.core.errors import AppError
from app.services.deepseek_provider import DeepSeekProvider


def test_deepseek_provider_posts_openai_compatible_json_with_mock_transport():
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["authorization"] = request.headers["Authorization"]
        captured["payload"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"content": '{"summary":"\u5206\u6790\u5b8c\u6210"}'}}
                ]
            },
        )

    provider = DeepSeekProvider("test-api-key", transport=httpx.MockTransport(handler))

    result = provider.complete_json("system prompt", "user prompt")

    assert result == {"summary": "\u5206\u6790\u5b8c\u6210"}
    assert captured["authorization"] == "Bearer test-api-key"
    assert captured["payload"] == {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "system prompt"},
            {"role": "user", "content": "user prompt"},
        ],
        "response_format": {"type": "json_object"},
    }


def test_deepseek_provider_maps_invalid_upstream_response_to_safe_app_error():
    provider = DeepSeekProvider(
        "test-api-key",
        transport=httpx.MockTransport(lambda _request: httpx.Response(502)),
    )

    with pytest.raises(AppError) as captured:
        provider.complete_json("system prompt", "user prompt")

    assert captured.value.code == "DEEPSEEK_PROVIDER_ERROR"
