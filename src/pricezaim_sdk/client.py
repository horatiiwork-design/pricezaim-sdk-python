"""HTTP-клиент публичного API pricezaim."""

from __future__ import annotations

import json
import time
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import httpx

from .exceptions import ApiError, TransportError
from .multipart import FileUpload, encode_form
from .retry import RetryPolicy

DEFAULT_BASE_URL = "https://api.pricezaim.ru"
DEFAULT_TIMEOUT = 15.0
VERSION = "0.1.0"


class Client:
    """Клиент API.

    :param api_key: API-ключ партнёра.
    :param base_url: базовый URL API.
    :param timeout: таймаут запроса в секундах.
    :param http_client: готовый ``httpx.Client`` (удобно для тестов и прокси).
    :param headers: дополнительные заголовки по умолчанию.
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        http_client: httpx.Client | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        """Создаёт клиент API."""
        api_key = api_key.strip()
        if not api_key:
            raise ValueError("API key must not be empty")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = float(timeout)
        self._http = http_client or httpx.Client(timeout=self.timeout)
        self._owns_http = http_client is None
        self._retry = RetryPolicy.from_env()
        self._default_headers = {
            "X-API-Key": self.api_key,
            "Accept": "application/json",
            "User-Agent": f"pricezaim-sdk-python/{VERSION}",
            **dict(headers or {}),
        }

        # Импорт здесь, чтобы избежать циклических импортов.
        from .resources.auctions import Auctions
        from .resources.bids import Bids
        from .resources.deals import Deals
        from .resources.webhooks import Webhooks

        self.auctions = Auctions(self)
        self.bids = Bids(self)
        self.deals = Deals(self)
        self.webhooks = Webhooks(self)

    def __enter__(self) -> Client:
        """Входит в context manager."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Закрывает клиент при выходе из context manager."""
        self.close()

    def close(self) -> None:
        """Закрывает собственный ``httpx.Client``."""
        if self._owns_http:
            self._http.close()

    def get(self, path: str, *, params: Mapping[str, Any] | None = None) -> dict[str, Any]:
        """Выполняет GET-запрос и возвращает JSON."""
        return self.send("GET", path, params=params)

    def post(
        self,
        path: str,
        payload: Mapping[str, Any] | None = None,
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Выполняет POST с JSON-телом."""
        return self.send(
            "POST",
            path,
            json_body=payload,
            idempotency_key=idempotency_key,
        )

    def put(self, path: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        """Выполняет PUT с JSON-телом."""
        return self.send("PUT", path, json_body=payload)

    def delete(self, path: str) -> dict[str, Any]:
        """Выполняет DELETE-запрос."""
        return self.send("DELETE", path)

    def post_multipart(
        self,
        path: str,
        *,
        data: Mapping[str, Any] | None = None,
        files: Sequence[FileUpload] = (),
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Выполняет POST с multipart/form-data."""
        return self.send(
            "POST",
            path,
            form=data,
            files=files,
            idempotency_key=idempotency_key,
            force_multipart=True,
        )

    def put_multipart(
        self,
        path: str,
        *,
        data: Mapping[str, Any] | None = None,
        files: Sequence[FileUpload] = (),
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Выполняет PUT с multipart/form-data."""
        return self.send(
            "PUT",
            path,
            form=data,
            files=files,
            idempotency_key=idempotency_key,
            force_multipart=True,
        )

    def send(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json_body: Mapping[str, Any] | None = None,
        form: Mapping[str, Any] | None = None,
        files: Sequence[FileUpload] = (),
        idempotency_key: str | None = None,
        force_multipart: bool = False,
    ) -> dict[str, Any]:
        """Отправляет запрос, обрабатывает ошибки и декодирует JSON."""
        response = self.request(
            method,
            self._url(path),
            params=params,
            json_body=json_body,
            form=form,
            files=files,
            idempotency_key=idempotency_key,
            force_multipart=force_multipart,
        )
        if response.status_code >= 400:
            raise ApiError.from_response(response)

        if not response.content:
            return {}

        try:
            data = response.json()
        except (json.JSONDecodeError, ValueError) as exc:
            raise ApiError(
                response.status_code,
                "API returned a non-JSON response",
                error_code="INVALID_RESPONSE",
                body={"raw": response.text},
                headers=dict(response.headers),
                request_id=response.headers.get("X-Request-Id"),
            ) from exc

        if not isinstance(data, dict):
            raise ApiError(
                response.status_code,
                "API returned a non-object JSON response",
                error_code="INVALID_RESPONSE",
                body={"raw": response.text},
                headers=dict(response.headers),
                request_id=response.headers.get("X-Request-Id"),
            )

        return data

    def send_raw(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> httpx.Response:
        """Отправляет запрос и возвращает сырой ответ (для файлов)."""
        response = self.request(method, self._url(path), params=params)
        if response.status_code >= 400:
            raise ApiError.from_response(response)
        return response

    def request(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, Any] | None = None,
        json_body: Mapping[str, Any] | None = None,
        form: Mapping[str, Any] | None = None,
        files: Sequence[FileUpload] = (),
        idempotency_key: str | None = None,
        force_multipart: bool = False,
    ) -> httpx.Response:
        """Выполняет HTTP-запрос с авторизацией и повторами по env-флагу."""
        headers = dict(self._default_headers)
        if idempotency_key is not None:
            headers["Idempotency-Key"] = idempotency_key

        attempts = self._retry.max_attempts if self._retry.enabled else 1
        for attempt in range(1, attempts + 1):
            handles, multipart = _open_files(files)
            content = None
            request_data = form
            # httpx отправляет пустой список файлов как urlencoded, поэтому
            # для multipart без файлов тело собирается вручную.
            if force_multipart and form is not None and not files:
                content, content_type = encode_form(form)
                request_data = None
                headers["Content-Type"] = content_type
            try:
                response = self._http.request(
                    method,
                    url,
                    params=_encode_params(params),
                    json=json_body,
                    content=content,
                    data=request_data,
                    files=multipart,
                    headers=headers,
                    timeout=self.timeout,
                )
            except httpx.RequestError as exc:
                if self._retry.allows_retry(method, headers, attempt):
                    time.sleep(self._retry.delay(attempt))
                    continue
                raise TransportError(str(exc)) from exc
            finally:
                for handle in handles:
                    handle.close()

            can_retry = self._retry.allows_retry(method, headers, attempt)
            if can_retry and self._retry.should_retry_status(response.status_code):
                retry_after = self._retry.parse_retry_after(response.headers.get("Retry-After", ""))
                time.sleep(self._retry.delay(attempt, retry_after))
                continue

            return response

        raise TransportError("HTTP request failed after retries")

    @property
    def retry_policy(self) -> RetryPolicy:
        """Текущая политика автоповторов."""
        return self._retry

    def _url(self, path: str) -> str:
        """Собирает абсолютный URL."""
        if path.startswith(("http://", "https://")):
            return path
        return f"{self.base_url}/{path.lstrip('/')}"


def _encode_params(params: Mapping[str, Any] | None) -> list[tuple[str, str]] | None:
    """Кодирует query-параметры, включая массивы."""
    if not params:
        return None

    encoded: list[tuple[str, str]] = []
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, (list, tuple, set)):
            field = key if key.endswith("[]") else f"{key}[]"
            encoded.extend((field, _param_value(item)) for item in value if item is not None)
        else:
            encoded.append((key, _param_value(value)))
    return encoded


def _param_value(value: Any) -> str:
    """Приводит значение query к строке."""
    if isinstance(value, bool):
        return "1" if value else "0"
    return str(value)


def _open_files(
    files: Sequence[FileUpload],
) -> tuple[list[Any], list[tuple[str, tuple[str, Any, str | None]]]]:
    """Открывает файлы для multipart и возвращает handles."""
    handles: list[Any] = []
    multipart: list[tuple[str, tuple[str, Any, str | None]]] = []
    for item in files:
        path = Path(item.path)
        if not path.is_file():
            for handle in handles:
                handle.close()
            raise FileNotFoundError(path)
        handle = path.open("rb")
        handles.append(handle)
        multipart.append(
            (
                item.field,
                (item.filename or path.name, handle, item.content_type),
            )
        )
    return handles, multipart
