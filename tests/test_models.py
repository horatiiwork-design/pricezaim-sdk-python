from __future__ import annotations

import pytest

from pricezaim_sdk import Auction, Bid, Deal, DealDocument, Page, Webhook


def test_auction_dto_maps_client_profile() -> None:
    data = {
        "id": 991,
        "title": "Auction",
        "status": "active",
        "can_bid": True,
        "required_amount": 600000,
        "client_profile": {
            "inn": "500100732259",
            "income_salary": 120000,
            "marketing_agreed": True,
        },
    }

    auction = Auction.from_dict(data)

    assert auction.id == 991
    assert auction.can_bid is True
    assert auction.required_amount == 600000.0
    assert auction.client_profile is not None
    assert auction.client_profile.inn == "500100732259"
    assert auction.client_profile.income_salary == 120000
    assert auction.client_profile.marketing_agreed is True
    assert auction.to_dict() == data


def test_auction_requires_id() -> None:
    with pytest.raises(ValueError):
        Auction.from_dict({"title": "No id"})


def test_bid_deal_and_webhook_dtos() -> None:
    bid = Bid.from_dict({"id": 477, "amount": 150000, "interest_rate": 19.5}, auction_id=991)
    assert bid.id == 477
    assert bid.auction_id == 991
    assert bid.amount == 150000.0

    deal = Deal.from_dict(
        {
            "id": 157,
            "auction_id": 991,
            "status": "active",
            "documents": [
                {"id": "doc-1", "original_name": "contract.pdf", "mime": "application/pdf"}
            ],
        }
    )
    assert deal.id == 157
    assert isinstance(deal.document_objects()[0], DealDocument)
    assert deal.document_objects()[0].original_name == "contract.pdf"

    webhook = Webhook.from_dict(
        {
            "id": 172,
            "url": "https://example.com/hook",
            "events": ["auction.started"],
            "has_secret": True,
        }
    )
    assert webhook.id == 172
    assert webhook.events == ["auction.started"]
    assert webhook.has_secret is True


def test_page_map() -> None:
    page = Page.from_dict(
        {"data": [{"id": 1}, {"id": 2}], "meta": {"total": 2, "current_page": 1, "last_page": 1}}
    )

    mapped = page.map(lambda item: item["id"])

    assert mapped.items == [1, 2]
    assert mapped.total == 2
    assert mapped.raw == page.raw
