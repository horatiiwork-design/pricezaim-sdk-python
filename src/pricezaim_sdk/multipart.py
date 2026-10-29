"""Описание файлов для multipart/form-data."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class FileUpload:
    """Файл для загрузки через multipart.

    :param field: имя поля формы, например ``photos[]``.
    :param path: путь к файлу на диске.
    :param filename: имя файла в запросе; по умолчанию имя файла на диске.
    :param content_type: MIME-тип; можно не указывать.
    """

    field: str
    path: str | Path
    filename: str | None = None
    content_type: str | None = None
