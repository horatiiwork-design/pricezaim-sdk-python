"""Пагинированный ответ API."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
from typing import Any, Generic, TypeVar

T = TypeVar("T")
U = TypeVar("U")


class Page(Generic[T]):
    """Страница результатов API: ``data`` + ``meta``."""

    def __init__(
        self,
        items: list[T],
        meta: Mapping[str, Any] | None = None,
        raw: Mapping[str, Any] | None = None,
    ) -> None:
        """Создаёт страницу результатов."""
        self._items = items
        self._meta = dict(meta or {})
        self._raw = dict(raw or {})

    @classmethod
    def from_dict(cls, response: Mapping[str, Any]) -> Page[Any]:
        """Создаёт страницу из ответа API."""
        data = response.get("data", [])
        items = list(data) if isinstance(data, list) else []
        meta = response.get("meta", {})
        meta = dict(meta) if isinstance(meta, Mapping) else {}
        for key in ("total", "current_page", "last_page", "per_page", "from", "to"):
            if key in response and key not in meta:
                meta[key] = response[key]
        return cls(items, meta, response)

    @property
    def items(self) -> list[T]:
        """Элементы текущей страницы."""
        return self._items

    @property
    def data(self) -> list[T]:
        """Псевдоним ``items``."""
        return self._items

    @property
    def meta(self) -> dict[str, Any]:
        """Метаданные пагинации."""
        return self._meta

    @property
    def raw(self) -> dict[str, Any]:
        """Исходный ответ API."""
        return self._raw

    @property
    def total(self) -> int:
        """Общее число записей."""
        return int(self._meta.get("total", len(self._items)))

    @property
    def current_page(self) -> int:
        """Номер текущей страницы."""
        return int(self._meta.get("current_page", 1))

    @property
    def last_page(self) -> int:
        """Номер последней страницы."""
        return int(self._meta.get("last_page", 1))

    @property
    def per_page(self) -> int:
        """Размер страницы."""
        return int(self._meta.get("per_page", len(self._items)))

    def is_empty(self) -> bool:
        """Проверяет, что страница пуста."""
        return not self._items

    def map(self, mapper: Callable[[T], U]) -> Page[U]:
        """Преобразует элементы, сохраняя meta и исходный ответ."""
        return Page([mapper(item) for item in self._items], self._meta, self._raw)

    def __iter__(self) -> Iterator[T]:
        """Итерирует элементы страницы."""
        return iter(self._items)

    def __len__(self) -> int:
        """Возвращает количество элементов на странице."""
        return len(self._items)

    def __getitem__(self, index: int) -> T:
        """Возвращает элемент страницы по индексу."""
        return self._items[index]
