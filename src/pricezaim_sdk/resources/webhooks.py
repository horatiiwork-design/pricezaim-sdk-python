"""Ресурс вебхуков."""

from __future__ import annotations

from typing import Any, Mapping

from ..models import Webhook
from ..page import Page
from .base import Resource


class Webhooks(Resource):
    """Методы управления вебхуками."""

    def list(self) -> dict[str, Any]:
        """Возвращает список вебхуков без секретов."""
        return self.client.get("/v1/webhooks")

    def list_dto(self) -> list[Webhook]:
        """Возвращает список вебхуков как DTO."""
        data = self.list().get("data", [])
        if not isinstance(data, list):
            return []
        return [Webhook.from_dict(item) for item in data if isinstance(item, Mapping)]

    def create(
        self,
        payload: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Создаёт вебхук."""
        return self.client.post("/v1/webhooks", payload, idempotency_key=idempotency_key)

    def create_dto(
        self,
        payload: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> Webhook:
        """Создаёт вебхук и возвращает DTO."""
        data = self.create(payload, idempotency_key=idempotency_key).get("data", {})
        return Webhook.from_dict(data if isinstance(data, Mapping) else {})

    def update(self, webhook_id: int | str, payload: Mapping[str, Any]) -> dict[str, Any]:
        """Обновляет вебхук."""
        return self.client.put(f"/v1/webhooks/{self._id(webhook_id)}", payload)

    def update_dto(self, webhook_id: int | str, payload: Mapping[str, Any]) -> Webhook:
        """Обновляет вебхук и возвращает DTO."""
        data = self.update(webhook_id, payload).get("data", {})
        return Webhook.from_dict(data if isinstance(data, Mapping) else {})

    def delete(self, webhook_id: int | str) -> dict[str, Any]:
        """Удаляет вебхук."""
        return self.client.delete(f"/v1/webhooks/{self._id(webhook_id)}")

    def test(self, webhook_id: int | str) -> dict[str, Any]:
        """Отправляет тестовый пинг вебхука."""
        return self.client.post(f"/v1/webhooks/{self._id(webhook_id)}/test")

    def deliveries(self, webhook_id: int | str, **filters: Any) -> Page[dict[str, Any]]:
        """Возвращает журнал доставок вебхука."""
        return Page.from_dict(
            self.client.get(f"/v1/webhooks/{self._id(webhook_id)}/deliveries", params=filters)
        )

    def retry_delivery(self, webhook_id: int | str, delivery_id: int | str) -> dict[str, Any]:
        """Повторяет доставку вебхука."""
        return self.client.post(
            f"/v1/webhooks/{self._id(webhook_id)}/deliveries/{self._id(delivery_id)}/retry"
        )
