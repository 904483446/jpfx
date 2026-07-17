from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import Settings, settings
from app.core.errors import search_not_configured, search_provider_error

_SEARCH_URL = "https://api.bochaai.com/v1/web-search"
_REQUEST_TIMEOUT_SECONDS = 15.0


@dataclass(frozen=True)
class SearchResult:
    title: str
    url: str
    summary: str


class BochaSearchProvider:
    def __init__(
        self,
        api_key: str | None = None,
        client: httpx.Client | None = None,
        *,
        settings: Settings = settings,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._api_key = api_key if api_key is not None else settings.bocha_api_key
        self._client = client
        self._transport = transport

    def search(self, query: str, *, limit: int = 10) -> list[SearchResult]:
        if not self._api_key:
            raise search_not_configured()

        try:
            if self._client is not None:
                response = self._client.post(
                    _SEARCH_URL,
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    json={"query": query, "count": limit},
                    timeout=_REQUEST_TIMEOUT_SECONDS,
                )
            else:
                with httpx.Client(
                    transport=self._transport,
                    timeout=_REQUEST_TIMEOUT_SECONDS,
                ) as client:
                    response = client.post(
                        _SEARCH_URL,
                        headers={"Authorization": f"Bearer {self._api_key}"},
                        json={"query": query, "count": limit},
                    )
            response.raise_for_status()
            return self._map_results(response.json(), limit=limit)
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as error:
            raise search_provider_error() from error

    @staticmethod
    def _map_results(payload: dict[str, Any], *, limit: int) -> list[SearchResult]:
        data = payload.get("data", payload)
        web_pages = data.get("webPages", data)
        values = web_pages.get("value", web_pages.get("items", []))
        if not isinstance(values, list):
            raise ValueError("Bocha search response has no result list")

        results: list[SearchResult] = []
        for item in values:
            if not isinstance(item, dict):
                continue
            title = str(item.get("name") or item.get("title") or "").strip()
            url = str(item.get("url") or item.get("link") or "").strip()
            summary = str(item.get("snippet") or item.get("summary") or "").strip()
            if title and url:
                results.append(SearchResult(title=title, url=url, summary=summary))
            if len(results) >= limit:
                break
        return results
