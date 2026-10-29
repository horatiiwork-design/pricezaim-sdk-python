"""Политика автоповторов."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(slots=True)
class RetryPolicy:
    """Параметры автоповторов.

    По умолчанию выключены. Включаются только env-флагом
    ``PRICEZAIM_SDK_RETRIES_ENABLED``.
    """

    enabled: bool = False
    max_attempts: int = 3
    base_delay_ms: int = 200

    def __post_init__(self) -> None:
        """Нормализует число попыток."""
        self.max_attempts = max(1, self.max_attempts)

    @classmethod
    def from_env(cls) -> RetryPolicy:
        """Создаёт политику из переменных окружения."""
        return cls(
            enabled=_env_bool("PRICEZAIM_SDK_RETRIES_ENABLED"),
            max_attempts=max(1, int(os.getenv("PRICEZAIM_SDK_RETRY_ATTEMPTS", "3"))),
            base_delay_ms=max(0, int(os.getenv("PRICEZAIM_SDK_RETRY_BASE_DELAY_MS", "200"))),
        )

    @classmethod
    def disabled(cls) -> RetryPolicy:
        """Возвращает выключенную политику."""
        return cls(enabled=False)

    def allows_retry(self, method: str, headers: Mapping[str, str], attempt: int) -> bool:
        """Проверяет, можно ли повторить запрос этим методом."""
        if not self.enabled or attempt >= self.max_attempts:
            return False

        method = method.upper()
        if method in {"GET", "HEAD", "PUT", "DELETE", "OPTIONS"}:
            return True

        if method in {"POST", "PATCH"}:
            return any(key.lower() == "idempotency-key" and value for key, value in headers.items())

        return False

    @staticmethod
    def should_retry_status(status: int) -> bool:
        """Является ли HTTP-статус временной ошибкой."""
        return status in {429, 500, 502, 503, 504}

    def delay(self, attempt: int, retry_after: int | None = None) -> float:
        """Возвращает задержку в секундах перед следующей попыткой."""
        if retry_after is not None:
            return min(30.0, max(0.0, float(retry_after)))
        return min(5.0, (self.base_delay_ms / 1000.0) * (2 ** max(0, attempt - 1)))

    @staticmethod
    def parse_retry_after(value: str) -> int | None:
        """Разбирает Retry-After: секунды или HTTP-дату."""
        if not value:
            return None
        if value.isdigit():
            return int(value)
        try:
            from datetime import datetime, timezone
            from email.utils import parsedate_to_datetime

            dt = parsedate_to_datetime(value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return max(0, int(dt.timestamp() - datetime.now(timezone.utc).timestamp()))
        except (TypeError, ValueError, OverflowError):
            return None


def _env_bool(name: str) -> bool:
    """Читает boolean-флаг из env."""
    value = os.getenv(name)
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}
