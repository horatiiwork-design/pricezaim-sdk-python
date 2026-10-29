"""Ресурс аукционов."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ..models import Auction
from ..multipart import FileUpload
from ..page import Page
from .base import Resource


class Auctions(Resource):
    """Методы работы с аукционами."""

    def list(self, **filters: Any) -> Page[dict[str, Any]]:
        """Возвращает доступные аукционы."""
        return Page.from_dict(self.client.get("/v1/auctions", params=filters))

    def my(self, **filters: Any) -> Page[dict[str, Any]]:
        """Возвращает аукционы своей организации."""
        return Page.from_dict(self.client.get("/v1/auctions/my", params=filters))

    def list_dto(self, **filters: Any) -> Page[Auction]:
        """Возвращает доступные аукционы как DTO."""
        return self.list(**filters).map(Auction.from_dict)

    def my_dto(self, **filters: Any) -> Page[Auction]:
        """Возвращает аукционы организации как DTO."""
        return self.my(**filters).map(Auction.from_dict)

    def get(self, auction_id: int | str) -> dict[str, Any]:
        """Возвращает карточку аукциона."""
        return self.client.get(f"/v1/auctions/{self._id(auction_id)}")

    def get_dto(self, auction_id: int | str) -> Auction:
        """Возвращает карточку аукциона как DTO."""
        return Auction.from_dict(self.get(auction_id))

    def create(
        self,
        payload: Mapping[str, Any],
        files: Sequence[FileUpload] = (),
    ) -> dict[str, Any]:
        """Создаёт аукцион в статусе draft."""
        return self.client.post_multipart(
            "/v1/auctions",
            data=payload,
            files=self._files(files),
        )

    def create_dto(
        self,
        payload: Mapping[str, Any],
        files: Sequence[FileUpload] = (),
    ) -> Auction:
        """Создаёт аукцион и возвращает DTO."""
        return Auction.from_dict(self.create(payload, files))

    def update(
        self,
        auction_id: int | str,
        payload: Mapping[str, Any],
        files: Sequence[FileUpload] = (),
    ) -> dict[str, Any]:
        """Изменяет аукцион своей организации."""
        path = f"/v1/auctions/{self._id(auction_id)}"
        if files:
            return self.client.put_multipart(path, data=payload, files=self._files(files))
        return self.client.put(path, payload)

    def update_dto(
        self,
        auction_id: int | str,
        payload: Mapping[str, Any],
        files: Sequence[FileUpload] = (),
    ) -> Auction:
        """Изменяет аукцион и возвращает DTO."""
        return Auction.from_dict(self.update(auction_id, payload, files))

    def start(self, auction_id: int | str) -> dict[str, Any]:
        """Запускает аукцион."""
        return self.client.post(f"/v1/auctions/{self._id(auction_id)}/start")

    def stop(self, auction_id: int | str) -> dict[str, Any]:
        """Останавливает аукцион."""
        return self.client.post(f"/v1/auctions/{self._id(auction_id)}/stop")

    def select_winner(self, auction_id: int | str, bid_id: int | str) -> dict[str, Any]:
        """Выбирает победителя по партнёрскому аукциону."""
        return self.client.post(
            f"/v1/auctions/{self._id(auction_id)}/winner",
            {"bid_id": bid_id},
        )

    def duplicate(self, auction_id: int | str) -> dict[str, Any]:
        """Помечает чужой аукцион как дубль."""
        return self.client.post(f"/v1/auctions/{self._id(auction_id)}/duplicate")

    def restore_duplicate(self, auction_id: int | str) -> dict[str, Any]:
        """Снимает пометку «дубль»."""
        return self.client.delete(f"/v1/auctions/{self._id(auction_id)}/duplicate")

    def refuse(self, auction_id: int | str, payload: Mapping[str, Any]) -> dict[str, Any]:
        """Отказывается от чужого активного аукциона."""
        return self.client.post(f"/v1/auctions/{self._id(auction_id)}/refusal", payload)

    def restore_refusal(self, auction_id: int | str) -> dict[str, Any]:
        """Снимает отказ от аукциона."""
        return self.client.delete(f"/v1/auctions/{self._id(auction_id)}/refusal")

    def photos(self, auction_id: int | str) -> dict[str, Any]:
        """Возвращает фото и файлы аукциона."""
        return self.client.get(f"/v1/auctions/{self._id(auction_id)}/photos")

    def download_file(self, auction_id: int | str, file_id: int | str) -> bytes:
        """Скачивает фото или файл аукциона."""
        return self.client.send_raw(
            "GET",
            f"/v1/auctions/{self._id(auction_id)}/files/{self._id(file_id)}",
        ).content
