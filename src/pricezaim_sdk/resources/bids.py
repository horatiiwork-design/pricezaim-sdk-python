"""Ресурс ставок."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..models import Bid
from ..page import Page
from .base import Resource


class Bids(Resource):
    """Методы работы со ставками."""

    def my(self, **filters: Any) -> Page[dict[str, Any]]:
        """Возвращает свои ставки."""
        return Page.from_dict(self.client.get("/v1/bids/my", params=filters))

    def my_dto(self, **filters: Any) -> Page[Bid]:
        """Возвращает свои ставки как DTO."""
        return self.my(**filters).map(Bid.from_dict)

    def for_auction(self, auction_id: int | str, **filters: Any) -> Page[dict[str, Any]]:
        """Возвращает актуальные ставки аукциона."""
        return Page.from_dict(
            self.client.get(f"/v1/auctions/{self._id(auction_id)}/bids", params=filters)
        )

    def for_auction_dto(self, auction_id: int | str, **filters: Any) -> Page[Bid]:
        """Возвращает ставки аукциона как DTO."""
        return self.for_auction(auction_id, **filters).map(
            lambda item: Bid.from_dict(item, auction_id=int(auction_id))
        )

    def place(
        self,
        auction_id: int | str,
        payload: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Размещает или заменяет ставку."""
        return self.client.post(
            f"/v1/auctions/{self._id(auction_id)}/bids",
            payload,
            idempotency_key=idempotency_key,
        )

    def place_dto(
        self,
        auction_id: int | str,
        payload: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> Bid:
        """Размещает ставку и возвращает DTO."""
        result = self.place(auction_id, payload, idempotency_key=idempotency_key)
        bid = result.get("bid", {})
        return Bid.from_dict(bid if isinstance(bid, Mapping) else {}, auction_id=int(auction_id))
