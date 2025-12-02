from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

from .config import CLIConfig, ConfigManager, get_token_from_env

LOGGER = logging.getLogger(__name__)

BASE_URL = "https://api.reg.ru/api/regru2"
RATE_LIMIT_ERRORS = {
    "IP_EXCEEDED_ALLOWED_CONNECTION_RATE": "Your IP exceeded the allowed request rate. Pause for a few minutes before retrying.",
    "ACCOUNT_EXCEEDED_ALLOWED_CONNECTION_RATE": "Your account exceeded the allowed request rate. Slow down your requests or retry later.",
}


class AuthenticationError(Exception):
    """Raised when authentication data is missing."""


class RateLimitError(Exception):
    """Raised when API responds with rate limit errors."""

    def __init__(self, code: str, message: str) -> None:
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


class RegruClient:
    def __init__(self, config_manager: Optional[ConfigManager] = None) -> None:
        self.config_manager = config_manager or ConfigManager()
        self.session = requests.Session()

    def _build_payload(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        token = get_token_from_env() or self.config_manager.config.token
        if not token:
            raise AuthenticationError(
                "No token found. Set REGRU_TOKEN or configure the CLI token."
            )

        merged: Dict[str, Any] = {
            "output_format": "json",
            "auth_token": token,
        }

        if self.config_manager.config.username:
            merged["username"] = self.config_manager.config.username

        if payload:
            merged.update(payload)
        return merged

    def _handle_response(self, response: requests.Response) -> APIResponse:
        LOGGER.info("%s %s", response.request.method, response.request.url)
        try:
            content = response.json()
        except ValueError:
            response.raise_for_status()
            raise

        LOGGER.debug("Response JSON: %s", content)

        if response.status_code == 429:
            raise RateLimitError(
                "HTTP_429", "Too many requests. Wait and retry with exponential backoff."
            )

        error_code = content.get("error_code")
        result = content.get("result", "error")
        message = content.get("error_text") or content.get("answer_text")

        if error_code in RATE_LIMIT_ERRORS:
            raise RateLimitError(error_code, RATE_LIMIT_ERRORS[error_code])

        api_response = APIResponse(result=result, data=content, message=message, error_code=error_code)
        if not api_response.is_success:
            LOGGER.error("API error %s: %s", error_code, message)
        return api_response

    def call_api(self, endpoint: str, payload: Optional[Dict[str, Any]] = None) -> APIResponse:
        url = f"{BASE_URL}/{endpoint}"
        body = self._build_payload(payload)
        LOGGER.debug("Request payload: %s", body)
        resp = self.session.post(url, json=body, timeout=30)
        return self._handle_response(resp)

    # Database operations
    def list_databases(self, **params: Any) -> APIResponse:
        return self.call_api("db/list", params)

    def create_database(
        self, domain_name: str, db_name: str, db_login: str, db_password: str
    ) -> APIResponse:
        payload = {
            "domain_name": domain_name,
            "db_name": db_name,
            "db_login": db_login,
            "db_password": db_password,
        }
        return self.call_api("db/create", payload)

    def modify_database(self, db_id: str, **changes: Any) -> APIResponse:
        payload = {"db_id": db_id}
        payload.update(changes)
        return self.call_api("db/modify", payload)
