"""Файлы и текстовые поля для multipart/form-data."""

from __future__ import annotations

import secrets
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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


def encode_form(form: Mapping[str, Any]) -> tuple[bytes, str]:
    """Собирает multipart-тело из текстовых полей."""
    boundary = secrets.token_hex(16)
    chunks: list[bytes] = []

    for raw_name, value in form.items():
        name = str(raw_name).replace("\r", "").replace("\n", "").replace('"', '\\"')
        values = value if isinstance(value, (list, tuple)) else [value]
        for item in values:
            if item is None:
                continue
            if isinstance(item, bool):
                item = "1" if item else "0"
            chunks.append(f"--{boundary}\r\n".encode())
            chunks.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
            chunks.append(str(item).encode("utf-8"))
            chunks.append(b"\r\n")

    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"
