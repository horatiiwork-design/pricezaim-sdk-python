from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from pricezaim_sdk import ApiError, Auction, Bid, Client, FileUpload, ValidationError, Webhook


def make_client(handler: Any, **kwargs: Any) -> Client:
    transport = httpx.MockTransport(handler)
    http = httpx.Client(transport=transport)
    return Client("test-key", base_url="https://api.test", http_client=http, **kwargs)


def test_list_sends_auth_query_and_returns_page() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["X-API-Key"] == "test-key"
        assert request.method == "GET"
        assert request.url.path == "/v1/auctions"
        assert "status=active" in str(request.url)
        assert "city%5B%5D=" in str(request.url)
        return httpx.Response(
            200,
            json={
                "data": [{"id": 10, "title": "Auction"}],
                "meta": {"total": 12, "current_page": 1, "last_page": 2, "per_page": 10},
            },
        )

    page = make_client(handler).auctions.list(status="active", city=["Москва", "Омск"])

    assert len(page) == 1
    assert page.total == 12
    assert page.last_page == 2
    assert page.items[0]["title"] == "Auction"


def test_validation_error_exposes_field_errors() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            422,
            json={
                "message": "The amount field is required.",
                "code": "VALIDATION_ERROR",
                "errors": {"amount": ["The amount field is required."]},
            },
            headers={"X-Request-Id": "req-422"},
        )

    with pytest.raises(ValidationError) as exc_info:
        make_client(handler).auctions.create({})

    error = exc_info.value
    assert error.status == 422
    assert error.error_code == "VALIDATION_ERROR"
    assert error.request_id == "req-422"
    assert error.errors == {"amount": ["The amount field is required."]}


def test_rate_limit_exposes_retry_after() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"message": "Too many requests"}, headers={"Retry-After": "7"})

    with pytest.raises(ApiError) as exc_info:
        make_client(handler).deals.get(1)

    assert exc_info.value.status == 429
    assert exc_info.value.is_rate_limited
    assert exc_info.value.retry_after == 7


def test_post_sends_idempotency_key() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.headers["Idempotency-Key"] == "idem-1"
        assert json.loads(request.content)["amount"] == 150000
        return httpx.Response(201, json={"success": True, "bid": {"id": 55}})

    result = make_client(handler).bids.place(10, {"amount": 150000}, idempotency_key="idem-1")

    assert result["bid"]["id"] == 55


def test_dto_methods() -> None:
    responses = iter(
        [
            httpx.Response(200, json={"id": 10, "title": "One", "status": "active"}),
            httpx.Response(
                200,
                json={
                    "data": [{"id": 10, "title": "One", "status": "active"}],
                    "meta": {"total": 1, "current_page": 1, "last_page": 1, "per_page": 15},
                },
            ),
            httpx.Response(201, json={"success": True, "bid": {"id": 55, "amount": 100}}),
            httpx.Response(
                200,
                json={"data": [{"id": 7, "url": "https://example.com", "events": ["auction.started"]}]},
            ),
        ]
    )

    client = make_client(lambda request: next(responses))

    auction = client.auctions.get_dto(10)
    assert isinstance(auction, Auction)
    assert auction.id == 10

    page = client.auctions.list_dto()
    assert isinstance(page.items[0], Auction)

    bid = client.bids.place_dto(10, {"amount": 100}, idempotency_key="idem-2")
    assert isinstance(bid, Bid)
    assert bid.auction_id == 10

    webhooks = client.webhooks.list_dto()
    assert isinstance(webhooks[0], Webhook)


def test_multipart_update_sends_file(tmp_path: Any) -> None:
    path = tmp_path / "photo.jpg"
    path.write_bytes(b"jpeg-bytes")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "PUT"
        assert request.headers["content-type"].startswith("multipart/form-data")
        assert b'name="photos[]"' in request.content
        assert b"jpeg-bytes" in request.content
        return httpx.Response(200, json={"id": 10, "title": "Updated"})

    result = make_client(handler).auctions.update(
        10,
        {"required_amount": 600000},
        [FileUpload("photos[]", path, "photo.jpg")],
    )

    assert result["title"] == "Updated"


def test_retries_are_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PRICEZAIM_SDK_RETRIES_ENABLED", raising=False)
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(500, json={"error": "temporary"})

    with pytest.raises(ApiError):
        make_client(handler).auctions.list()

    assert calls == 1


def test_get_retries_500_when_env_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PRICEZAIM_SDK_RETRIES_ENABLED", "1")
    monkeypatch.setenv("PRICEZAIM_SDK_RETRY_BASE_DELAY_MS", "0")
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(500, json={"error": "temporary"})
        return httpx.Response(200, json={"data": []})

    make_client(handler).auctions.list()

    assert calls == 2


def test_transport_error_is_retried(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PRICEZAIM_SDK_RETRIES_ENABLED", "1")
    monkeypatch.setenv("PRICEZAIM_SDK_RETRY_BASE_DELAY_MS", "0")
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise httpx.ConnectError("connection refused", request=request)
        return httpx.Response(200, json={"data": []})

    make_client(handler).auctions.list()

    assert calls == 2


def test_post_without_idempotency_key_is_not_retried(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PRICEZAIM_SDK_RETRIES_ENABLED", "1")
    monkeypatch.setenv("PRICEZAIM_SDK_RETRY_BASE_DELAY_MS", "0")
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(500, json={"error": "temporary"})

    with pytest.raises(ApiError):
        make_client(handler).bids.place(10, {"amount": 1})

    assert calls == 1


def test_post_with_idempotency_key_is_retried(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PRICEZAIM_SDK_RETRIES_ENABLED", "1")
    monkeypatch.setenv("PRICEZAIM_SDK_RETRY_BASE_DELAY_MS", "0")
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(500, json={"error": "temporary"})
        return httpx.Response(201, json={"success": True, "bid": {"id": 1}})

    result = make_client(handler).bids.place(10, {"amount": 1}, idempotency_key="idem-3")

    assert calls == 2
    assert result["bid"]["id"] == 1


def test_get_retries_429_with_retry_after(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PRICEZAIM_SDK_RETRIES_ENABLED", "1")
    monkeypatch.setenv("PRICEZAIM_SDK_RETRY_BASE_DELAY_MS", "0")
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(429, json={"message": "slow down"}, headers={"Retry-After": "0"})
        return httpx.Response(200, json={"data": []})

    make_client(handler).auctions.list()

    assert calls == 2


def test_query_booleans_are_encoded_as_1_or_0() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert "active=1" in str(request.url)
        assert "archived=0" in str(request.url)
        return httpx.Response(200, json={"data": []})

    make_client(handler).auctions.list(active=True, archived=False)
