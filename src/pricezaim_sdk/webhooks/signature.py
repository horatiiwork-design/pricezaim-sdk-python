"""Проверка подписи входящих вебхуков."""

from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timezone
from typing import Any, Mapping


def sign(payload: str | bytes, secret: str) -> str:
    """Считает HMAC-SHA256 подпись для сырого тела."""
    return hmac.new(secret.encode("utf-8"), _as_bytes(payload), hashlib.sha256).hexdigest()


def verify(
    payload: str | bytes,
    secret: str,
    signature: str,
    timestamp: str | None = None,
    tolerance: int = 300,
) -> bool:
    """Проверяет HMAC-SHA256 подпись."""
    if not secret or not signature:
        return False

    if tolerance > 0 and timestamp:
        try:
            sent_at = _parse_timestamp(timestamp)
        except ValueError:
            return False
        if abs(datetime.now(timezone.utc).timestamp() - sent_at) > tolerance:
            return False

    expected = sign(payload, secret)
    return hmac.compare_digest(expected, signature.lower())


def verify_request(
    payload: str | bytes,
    secret: str,
    headers: Mapping[str, Any],
    tolerance: int = 300,
) -> bool:
    """Проверяет подпись по заголовкам запроса."""
    signature = _header(headers, "X-Webhook-Signature")
    if not signature:
        return False
    return verify(payload, secret, signature, _header(headers, "X-Webhook-Timestamp"), tolerance)


def _as_bytes(payload: str | bytes) -> bytes:
    """Приводит тело к bytes."""
    return payload if isinstance(payload, bytes) else payload.encode("utf-8")


def _header(headers: Mapping[str, Any], name: str) -> str | None:
    """Ищет заголовок без учёта регистра."""
    target = name.lower()
    server_key = "http_" + target.replace("-", "_")
    for key, value in headers.items():
        normalized = str(key).lower()
        if normalized not in {target, server_key}:
            continue
        if isinstance(value, (list, tuple)):
            value = value[0] if value else None
        return str(value) if value is not None else None
    return None


def _parse_timestamp(value: str) -> float:
    """Разбирает ISO-8601 timestamp."""
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()
