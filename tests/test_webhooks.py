from __future__ import annotations

from datetime import datetime, timedelta, timezone

from pricezaim_sdk import WebhookEvent, WebhookEventType, sign, verify, verify_request


def test_signature_and_request_headers() -> None:
    payload = '{"event":"auction.started"}'
    secret = "super-secret"
    signature = sign(payload, secret)
    timestamp = datetime.now(timezone.utc).isoformat()

    assert verify(payload, secret, signature, timestamp)
    assert verify_request(payload, secret, {"X-Webhook-Signature": signature, "X-Webhook-Timestamp": timestamp})
    assert verify_request(payload, secret, {"HTTP_X_WEBHOOK_SIGNATURE": signature, "HTTP_X_WEBHOOK_TIMESTAMP": timestamp})


def test_signature_rejects_tampering_and_old_timestamp() -> None:
    payload = '{"id":1}'
    secret = "super-secret"
    signature = sign(payload, secret)
    old = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()

    assert not verify(payload + " ", secret, signature)
    assert not verify(payload, secret, signature, old)
    assert not verify_request(payload, secret, {})


def test_event_getters_and_types() -> None:
    event = WebhookEvent.from_json(
        '{"event_id":"evt-1","event":"auction.started","auction":{"id":1022}}'
    )

    assert event.event_id == "evt-1"
    assert event.name == "auction.started"
    assert event.type is WebhookEventType.AUCTION_STARTED
    assert event.is_known is True
    assert event.is_(WebhookEventType.AUCTION_STARTED)
    assert event.is_("auction.started")
    assert event.auction_id == 1022


def test_event_unknown_and_numeric_id() -> None:
    event = WebhookEvent.from_dict({"event_id": 73, "event": "future.event", "deal": {"auction_id": 1008}})

    assert event.event_id == "73"
    assert event.type is None
    assert event.is_known is False
    assert event.auction_id == 1008


def test_event_catalog() -> None:
    assert len(WebhookEventType) == 17
    assert WebhookEventType.is_known("auction.started")
    assert WebhookEventType.is_known("webhook.test")
    assert not WebhookEventType.is_known("auction.created")
