# Справочник методов

## Client

```python
Client(api_key, *, base_url="https://api.pricezaim.ru", timeout=15.0,
       http_client=None, headers=None)
```

| Метод | Назначение |
|---|---|
| `client.auctions` | ресурс аукционов |
| `client.bids` | ресурс ставок |
| `client.deals` | ресурс сделок |
| `client.webhooks` | ресурс вебхуков |
| `client.get(path, params=...)` | GET |
| `client.post(path, payload=..., idempotency_key=...)` | POST с JSON |
| `client.post_multipart(path, data=..., files=...)` | POST с файлами |
| `client.put(path, payload)` | PUT с JSON |
| `client.put_multipart(path, data=..., files=...)` | PUT с файлами |
| `client.delete(path)` | DELETE |
| `client.send(...)` | запрос с JSON-ответом |
| `client.send_raw(...)` | `httpx.Response` |
| `client.request(...)` | низкоуровневый запрос |
| `client.close()` | закрыть HTTP-клиент |
| `client.retry_policy` | текущая политика повторов |

## Аукционы

| Метод | Возвращает |
|---|---|
| `list(**filters)` | `Page[dict]` |
| `my(**filters)` | `Page[dict]` |
| `list_dto(**filters)` | `Page[Auction]` |
| `my_dto(**filters)` | `Page[Auction]` |
| `get(auction_id)` | `dict` |
| `get_dto(auction_id)` | `Auction` |
| `create(payload, files=...)` | `dict` |
| `create_dto(payload, files=...)` | `Auction` |
| `update(auction_id, payload, files=...)` | `dict` |
| `update_dto(auction_id, payload, files=...)` | `Auction` |
| `start(auction_id)` | `dict` |
| `stop(auction_id)` | `dict` |
| `select_winner(auction_id, bid_id)` | `dict` |
| `duplicate(auction_id)` | `dict` |
| `restore_duplicate(auction_id)` | `dict` |
| `refuse(auction_id, payload)` | `dict` |
| `restore_refusal(auction_id)` | `dict` |
| `photos(auction_id)` | `dict` |
| `download_file(auction_id, file_id)` | `bytes` |

Файл передаётся через `FileUpload`:

```python
from pricezaim_sdk import FileUpload

client.auctions.update(
    991,
    {"required_amount": 600000},
    [FileUpload("photos[]", "/tmp/photo.jpg", "photo.jpg")],
)
```

`filters` — query-параметры API: `status`, `city`, `city[]`, `date_from`,
`date_to`, `page`, `per_page` и другие.

## Ставки

| Метод | Возвращает |
|---|---|
| `my(**filters)` | `Page[dict]` |
| `my_dto(**filters)` | `Page[Bid]` |
| `for_auction(auction_id, **filters)` | `Page[dict]` |
| `for_auction_dto(auction_id, **filters)` | `Page[Bid]` |
| `place(auction_id, payload, idempotency_key=...)` | `dict` |
| `place_dto(auction_id, payload, idempotency_key=...)` | `Bid` |

`payload`: `amount`, `interest_rate`, `term`, `comment`.

## Сделки

| Метод | Возвращает |
|---|---|
| `list(**filters)` | `Page[dict]` |
| `list_dto(**filters)` | `Page[Deal]` |
| `get(deal_id)` | `dict` |
| `get_dto(deal_id)` | `Deal` |
| `documents(deal_id)` | `dict` |
| `documents_dto(deal_id)` | `list[DealDocument]` |
| `upload_documents(deal_id, files, fields=..., idempotency_key=...)` | `dict` |
| `requisites(deal_id)` | `dict` |
| `approve(deal_id, payload=..., idempotency_key=...)` | `dict` |
| `chat(deal_id, **filters)` | `dict` |
| `send_chat(deal_id, message, payload=..., idempotency_key=...)` | `dict` |
| `download_document(deal_id, document_id)` | `bytes` |
| `delete_document(deal_id, document_id)` | `dict` |

## Вебхуки

| Метод | Возвращает |
|---|---|
| `list()` | `dict` |
| `list_dto()` | `list[Webhook]` |
| `create(payload, idempotency_key=...)` | `dict` |
| `create_dto(payload, idempotency_key=...)` | `Webhook` |
| `update(webhook_id, payload)` | `dict` |
| `update_dto(webhook_id, payload)` | `Webhook` |
| `delete(webhook_id)` | `dict` |
| `test(webhook_id)` | `dict` |
| `deliveries(webhook_id, **filters)` | `Page[dict]` |
| `retry_delivery(webhook_id, delivery_id)` | `dict` |

## Page

`Page` поддерживает `len()`, `iter()`, индексацию и `map()`.

| Свойство / метод | Возвращает |
|---|---|
| `items` / `data` | `list` |
| `meta` | `dict` |
| `raw` | `dict` |
| `total` | `int` |
| `current_page` | `int` |
| `last_page` | `int` |
| `per_page` | `int` |
| `is_empty()` | `bool` |
| `map(fn)` | `Page` |

## DTO

Все DTO имеют `from_dict()` и `to_dict()`. `to_dict()` возвращает исходный
ответ API.

| DTO | Поля |
|---|---|
| `Auction` | `id`, `uuid`, `status`, `required_amount`, `can_bid`, `client_profile` |
| `ClientProfile` | `inn`, `passport_number`, `income_salary`; содержит ПДн |
| `Bid` | `id`, `auction_id`, `amount`, `interest_rate`, `term` |
| `Deal` | `id`, `auction_id`, `status`, `documents`, `document_objects()` |
| `DealDocument` | `id`, `original_name`, `mime`, `size` |
| `Webhook` | `id`, `url`, `events`, `active`, `has_secret` |

## Вебхуки: подпись и событие

```python
sign(payload, secret) -> str
verify(payload, secret, signature, timestamp=None, tolerance=300) -> bool
verify_request(payload, secret, headers, tolerance=300) -> bool

WebhookEvent.from_json(raw)
WebhookEvent.from_dict(payload)

event.event_id
event.name
event.type
event.is_known
event.auction_id
event.payload
event.to_dict()
event.is_(event_type)
```

## Повторы

| Ситуация | Повтор |
|---|---|
| `429`, `500`, `502`, `503`, `504` | да |
| сеть или таймаут | да |
| `GET`, `HEAD`, `PUT`, `DELETE`, `OPTIONS` | да |
| `POST`, `PATCH` без `idempotency_key` | нет |
| `POST`, `PATCH` с `idempotency_key` | да |
| `400`, `401`, `403`, `404`, `422` | нет |

Включаются переменной `PRICEZAIM_SDK_RETRIES_ENABLED`. Дополнительно:
`PRICEZAIM_SDK_RETRY_ATTEMPTS`, `PRICEZAIM_SDK_RETRY_BASE_DELAY_MS`.

## Исключения

`ApiError` — HTTP-ошибка или не-JSON ответ. Доступны `status`, `error_code`,
`body`, `headers`, `request_id`, `retry_after`, `is_rate_limited`.

`ValidationError` — ответ `422`, ошибки полей в `errors`.

`TransportError` — сеть, DNS, таймаут, TLS.
