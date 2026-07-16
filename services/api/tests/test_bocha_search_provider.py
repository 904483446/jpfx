import httpx
import pytest
from app.core.config import Settings
from app.core.errors import AppError
from app.services.bocha_search_provider import BochaSearchProvider


def test_search_maps_bocha_results_without_exposing_key():
    captured_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(
            200,
            json={
                "code": 200,
                "data": {
                    "webPages": {
                        "value": [
                            {
                                "name": "Example Product",
                                "url": "https://example.com/product",
                                "snippet": "An AI writing product.",
                            }
                        ]
                    }
                },
            },
        )

    provider = BochaSearchProvider(
        settings=Settings(_env_file=None, bocha_api_key="test-key"),
        transport=httpx.MockTransport(handler),
    )

    result = provider.search("AI writing", limit=3)

    assert [(item.title, item.url, item.summary) for item in result] == [
        ("Example Product", "https://example.com/product", "An AI writing product.")
    ]
    assert captured_request is not None
    assert captured_request.url == "https://api.bochaai.com/v1/web-search"
    assert captured_request.headers["Authorization"] == "Bearer test-key"
    assert "test-key" not in repr(result)


def test_search_rejects_missing_key_without_making_request():
    provider = BochaSearchProvider(settings=Settings(_env_file=None))

    with pytest.raises(AppError) as captured:
        provider.search("AI writing")

    assert captured.value.code == "SEARCH_NOT_CONFIGURED"


def test_search_maps_upstream_failure_without_exposing_key():
    provider = BochaSearchProvider(
        settings=Settings(_env_file=None, bocha_api_key="secret-key"),
        transport=httpx.MockTransport(lambda request: httpx.Response(429)),
    )

    with pytest.raises(AppError) as captured:
        provider.search("AI writing")

    assert captured.value.code == "SEARCH_PROVIDER_ERROR"
    assert "secret-key" not in str(captured.value)
