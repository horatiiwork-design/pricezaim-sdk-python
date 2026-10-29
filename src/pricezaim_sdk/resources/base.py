"""Базовый класс ресурса."""

from __future__ import annotations

from collections.abc import Sequence
from urllib.parse import quote

from ..client import Client
from ..multipart import FileUpload


class Resource:
    """Ресурс, привязанный к клиенту API."""

    def __init__(self, client: Client) -> None:
        """Создаёт ресурс."""
        self.client = client

    @staticmethod
    def _id(value: int | str) -> str:
        """Кодирует идентификатор для пути URL."""
        return quote(str(value), safe="")

    @staticmethod
    def _files(files: Sequence[FileUpload]) -> tuple[FileUpload, ...]:
        """Нормализует список файлов."""
        return tuple(files)
