"""Ресурс сделок."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ..models import Deal, DealDocument
from ..multipart import FileUpload
from ..page import Page
from .base import Resource

DealDocumentList = list[DealDocument]


class Deals(Resource):
    """Методы работы со сделками."""

    def list(self, **filters: Any) -> Page[dict[str, Any]]:
        """Возвращает список сделок."""
        return Page.from_dict(self.client.get("/v1/deals", params=filters))

    def list_dto(self, **filters: Any) -> Page[Deal]:
        """Возвращает сделки как DTO."""
        return self.list(**filters).map(Deal.from_dict)

    def get(self, deal_id: int | str) -> dict[str, Any]:
        """Возвращает карточку сделки."""
        return self.client.get(f"/v1/deals/{self._id(deal_id)}")

    def get_dto(self, deal_id: int | str) -> Deal:
        """Возвращает карточку сделки как DTO."""
        return Deal.from_dict(self.get(deal_id))

    def documents(self, deal_id: int | str) -> dict[str, Any]:
        """Возвращает список документов сделки."""
        return self.client.get(f"/v1/deals/{self._id(deal_id)}/documents")

    def documents_dto(self, deal_id: int | str) -> DealDocumentList:
        """Возвращает документы сделки как DTO."""
        data = self.documents(deal_id).get("data", [])
        if not isinstance(data, list):
            return []
        return [DealDocument.from_dict(item) for item in data if isinstance(item, Mapping)]

    def upload_documents(
        self,
        deal_id: int | str,
        files: Sequence[FileUpload],
        fields: Mapping[str, Any] | None = None,
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Загружает документы в сделку."""
        return self.client.post_multipart(
            f"/v1/deals/{self._id(deal_id)}/documents",
            data=fields,
            files=self._files(files),
            idempotency_key=idempotency_key,
        )

    def requisites(self, deal_id: int | str) -> dict[str, Any]:
        """Возвращает реквизиты сделки."""
        return self.client.get(f"/v1/deals/{self._id(deal_id)}/requisites")

    def approve(
        self,
        deal_id: int | str,
        payload: Mapping[str, Any] | None = None,
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Согласует сделку со стороны организации."""
        return self.client.post(
            f"/v1/deals/{self._id(deal_id)}/approve",
            payload,
            idempotency_key=idempotency_key,
        )

    def chat(self, deal_id: int | str, **filters: Any) -> dict[str, Any]:
        """Возвращает историю чата сделки."""
        return self.client.get(f"/v1/deals/{self._id(deal_id)}/chat", params=filters)

    def send_chat(
        self,
        deal_id: int | str,
        message: str,
        payload: Mapping[str, Any] | None = None,
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Отправляет сообщение в чат сделки."""
        body = dict(payload or {})
        body["message"] = message
        return self.client.post(
            f"/v1/deals/{self._id(deal_id)}/chat",
            body,
            idempotency_key=idempotency_key,
        )

    def download_document(self, deal_id: int | str, document_id: int | str) -> bytes:
        """Скачивает документ сделки."""
        return self.client.send_raw(
            "GET",
            f"/v1/deals/{self._id(deal_id)}/documents/{self._id(document_id)}",
        ).content

    def delete_document(self, deal_id: int | str, document_id: int | str) -> dict[str, Any]:
        """Удаляет документ сделки."""
        return self.client.delete(
            f"/v1/deals/{self._id(deal_id)}/documents/{self._id(document_id)}"
        )
