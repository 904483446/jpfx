import httpx

from app.core.errors import AppError, deepseek_provider_error

_CHAT_COMPLETIONS_URL = "https://api.deepseek.com/chat/completions"
_DEFAULT_MODEL = "deepseek-chat"
_REQUEST_TIMEOUT_SECONDS = 30.0


class DeepSeekProvider:
    def __init__(
        self,
        api_key: str,
        *,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._api_key = api_key
        self._transport = transport

    def complete_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
        try:
            with httpx.Client(
                transport=self._transport, timeout=_REQUEST_TIMEOUT_SECONDS
            ) as client:
                response = client.post(
                    _CHAT_COMPLETIONS_URL,
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    json={
                        "model": _DEFAULT_MODEL,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "response_format": {"type": "json_object"},
                    },
                )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            result = httpx.Response(200, content=content).json()
            if not isinstance(result, dict):
                raise TypeError("DeepSeek JSON result must be an object")
            return result
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as error:
            if isinstance(error, AppError):
                raise
            raise deepseek_provider_error() from error
