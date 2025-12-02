"""HTTP-клиент для работы с REG.RU API."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx

from .config import Settings


class AuthenticationError(Exception):
    """Исключение при отсутствии токена."""


class RateLimitError(Exception):
    """Ошибка превышения лимита запросов."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class APIError(Exception):
    """Любая ошибка, вернувшаяся от API."""

    def __init__(self, message: str, code: Optional[str] = None) -> None:
        super().__init__(message)
        self.code = code


@dataclass
class APIResponse:
    result: str
    data: Dict[str, Any]
    message: Optional[str] = None
    error_code: Optional[str] = None

    @property
    def is_success(self) -> bool:
        return self.result.lower() == "success"


RATE_LIMIT_ERRORS = {
    "IP_EXCEEDED_ALLOWED_CONNECTION_RATE": "Превышено число запросов с этого IP. Подождите и повторите попытку позже.",
    "ACCOUNT_EXCEEDED_ALLOWED_CONNECTION_RATE": "Аккаунт превысил допустимую частоту запросов. Уменьшите нагрузку и попробуйте снова.",
}


class RegruClient:
    """Обёртка над httpx для выполнения запросов к REG.RU."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client = httpx.Client(
            base_url=self.settings.base_url,
            headers={"User-Agent": "regru-api-cli/0.1.0"},
        )

    def _build_payload(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.settings.token:
            raise AuthenticationError(
                "Не указан токен. Передайте его через REGRU_API_TOKEN или команду config set-token."
            )

        body: Dict[str, Any] = {
            "auth_token": self.settings.token,
            "output_format": "json",
        }
        if self.settings.username:
            body["username"] = self.settings.username
        if payload:
            body.update(payload)
        return body

    def _handle_response(self, response: httpx.Response) -> APIResponse:
        if response.status_code == httpx.codes.TOO_MANY_REQUESTS:
            raise RateLimitError("HTTP_429", "Превышен лимит запросов. Подождите и повторите попытку.")

        try:
            content = response.json()
        except json.JSONDecodeError as exc:
            raise APIError(f"Некорректный JSON: {response.text}") from exc

        error_code = content.get("error_code")
        result = content.get("result", "error")
        message = content.get("error_text") or content.get("answer_text")

        if error_code in RATE_LIMIT_ERRORS:
            raise RateLimitError(error_code, RATE_LIMIT_ERRORS[error_code])

        api_response = APIResponse(result=result, data=content, message=message, error_code=error_code)
        if not api_response.is_success and message:
            raise APIError(message, code=error_code)
        return api_response

    def _post(self, endpoint: str, payload: Optional[Dict[str, Any]] = None) -> APIResponse:
        body = self._build_payload(payload)
        response = self._client.post(endpoint, json=body, timeout=30)
        return self._handle_response(response)

    def ping(self) -> APIResponse:
        return self._post("user/nop")

    def list_services(self) -> APIResponse:
        return self._post("service/get_list")

    def list_servers(self) -> APIResponse:
        return self._post("hosting/get_servers")

