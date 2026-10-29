"""Исключения SDK."""

from __future__ import annotations

import json
from typing import Any, Mapping

import httpx


class PricezaimError(Exception):
    """Базовая ошибка SDK."""


class TransportError(PricezaimError):
    """Сетевая ошибка, таймаут или ошибка транспорта."""


class ApiError(PricezaimError):
    """HTTP-ошибка API."""

    def __init__(
        self,
        status: int,
        message: str,
        *,
        error_code: str | None = None,
        body: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        request_id: str | None = None,
        retry_after: int | None = None,
    ) -> None:
        """Создаёт исключение."""
        super().__init__(message)
        self.status = status
        self.message = message
        self.error_code = error_code
        self.body: dict[str, Any] = dict(body or {})
        self.headers: dict[str, str] = dict(headers or {})
        self.request_id = request_id
        self.retry_after = retry_after

    @classmethod
    def from_response(
        cls,
        response: httpx.Response,
        raw_body: str | None = None,
    ) -> ApiError:
        """Создаёт исключение из httpx.Response."""
        raw = raw_body if raw_body is not None else response.text
        try:
            body = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            body = {}
        if not isinstance(body, dict):
            body = {}

        message = str(
            body.get("message")
            or body.get("detail")
            or body.get("error")
            or "API request failed"
        )
        error_code = str(body["code"]) if body.get("code") is not None else None
        request_id = response.headers.get("X-Request-Id")
        retry_after = _parse_retry_after(response.headers.get("Retry-After", ""))
        headers = {key: value for key, value in response.headers.items()}

        if response.status_code == 422:
            errors = body.get("errors")
            return ValidationError(
                response.status_code,
                message,
                error_code=error_code,
                body=body,
                headers=headers,
                request_id=request_id,
                retry_after=retry_after,
                errors=errors if isinstance(errors, dict) else {},
            )

        return cls(
            response.status_code,
            message,
            error_code=error_code,
            body=body,
            headers=headers,
            request_id=request_id,
            retry_after=retry_after,
        )

    @property
    def is_rate_limited(self) -> bool:
        """Является ли ошибка 429."""
        return self.status == 429


class ValidationError(ApiError):
    """Ошибка валидации 422 с ошибками полей."""

    def __init__(self, *args: Any, errors: Mapping[str, Any] | None = None, **kwargs: Any) -> None:
        """Создаёт исключение."""
        super().__init__(*args, **kwargs)
        self.errors: dict[str, Any] = dict(errors or {})


def _parse_retry_after(value: str) -> int | None:
    """Разбирает Retry-After."""
    if not value:
        return None
    if value.isdigit():
        return int(value)
    try:
        from email.utils import parsedate_to_datetime
        from datetime import datetime, timezone

        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return max(0, int(dt.timestamp() - datetime.now(timezone.utc).timestamp()))
    except (TypeError, ValueError, OverflowError):
        return None
