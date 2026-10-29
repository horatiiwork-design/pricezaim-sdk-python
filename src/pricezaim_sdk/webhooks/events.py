"""Типы и разбор входящих вебхуков."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class WebhookEventType(str, Enum):
    """Известные события pricezaim."""

    DEAL_CREATED = "deal.created"
    DEAL_APPROVED = "deal.approved"
    DEAL_CLOSED = "deal.closed"
    DEAL_DOCUMENTS_UPLOADED = "deal.documents_uploaded"

    AUCTION_STARTED = "auction.started"
    AUCTION_ENDED = "auction.ended"
    AUCTION_CLOSED = "auction.closed"
    AUCTION_RESTARTED = "auction.restarted"
    AUCTION_CANCELLED = "auction.cancelled"

    CHAT_AUCTION_MESSAGE = "chat.auction_message"
    CHAT_DEAL_MESSAGE = "chat.deal_message"
    CHAT_SUPPORT_MESSAGE = "chat.support_message"

    BID_PLACED_OWN = "bid.placed.own"
    BID_PLACED_ANY = "bid.placed.any"
    BID_PLACED_PARTICIPATING = "bid.placed.participating"
    BID_OUTBID = "bid.outbid"

    WEBHOOK_TEST = "webhook.test"

    @classmethod
    def values(cls) -> list[str]:
        """Возвращает все известные имена событий."""
        return [item.value for item in cls]

    @classmethod
    def is_known(cls, name: str) -> bool:
        """Проверяет, известно ли имя события."""
        try:
            cls(name)
        except ValueError:
            return False
        return True


@dataclass(frozen=True, slots=True)
class WebhookEvent:
    """Разобранный конверт вебхука."""

    event_id: str
    name: str
    payload: dict[str, Any]
    auction_id: int | None = None

    @classmethod
    def from_json(cls, raw: str | bytes) -> WebhookEvent:
        """Разбирает JSON-тело вебхука."""
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError("Webhook payload is not valid JSON") from exc
        if not isinstance(data, dict):
            raise ValueError("Webhook payload must be a JSON object")
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> WebhookEvent:
        """Создаёт событие из массива."""
        event_id = payload.get("event_id")
        if isinstance(event_id, bool) or not isinstance(event_id, (str, int)):
            raise ValueError("Webhook payload must contain a string or integer event_id")
        event_id = str(event_id).strip()
        if not event_id:
            raise ValueError("Webhook event_id must not be empty")

        name = payload.get("event")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Webhook payload must contain a non-empty event")

        return cls(
            event_id=event_id,
            name=name.strip(),
            payload=dict(payload),
            auction_id=_extract_auction_id(payload),
        )

    @property
    def type(self) -> WebhookEventType | None:
        """Известный тип события или None."""
        try:
            return WebhookEventType(self.name)
        except ValueError:
            return None

    @property
    def is_known(self) -> bool:
        """Известно ли событие текущей версии SDK."""
        return self.type is not None

    def is_(self, event_type: WebhookEventType | str) -> bool:
        """Сравнивает событие с типом или именем."""
        name = event_type.value if isinstance(event_type, WebhookEventType) else event_type
        return self.name == name

    def to_dict(self) -> dict[str, Any]:
        """Возвращает полный конверт."""
        return dict(self.payload)


def _extract_auction_id(payload: Mapping[str, Any]) -> int | None:
    """Ищет ID аукциона в конверте."""
    auction = payload.get("auction")
    deal = payload.get("deal")
    candidates = [
        auction.get("id") if isinstance(auction, Mapping) else None,
        payload.get("auction_id"),
        deal.get("auction_id") if isinstance(deal, Mapping) else None,
    ]
    for candidate in candidates:
        if isinstance(candidate, bool):
            continue
        if isinstance(candidate, int):
            return candidate
        if isinstance(candidate, str) and candidate.isdigit():
            return int(candidate)
    return None
