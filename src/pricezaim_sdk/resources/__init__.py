"""Ресурсы API."""

from .auctions import Auctions
from .bids import Bids
from .deals import Deals
from .webhooks import Webhooks

__all__ = ["Auctions", "Bids", "Deals", "Webhooks"]
