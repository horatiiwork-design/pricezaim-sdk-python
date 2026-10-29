# pricezaim Python SDK

Python-клиент для публичного API [pricezaim](https://api.pricezaim.ru/docs).

- авторизация по `X-API-Key`;
- синхронный HTTP-клиент на `httpx`;
- ресурсы `auctions`, `bids`, `deals`, `webhooks`;
- DTO для основных сущностей;
- пагинация;
- проверка HMAC-подписи вебхуков;
- opt-in автоповторы;
- `Idempotency-Key` для безопасных повторов.

Требования: Python 3.10+.

## Установка

```bash
pip install pricezaim-sdk
```

Пока пакет не опубликован в PyPI, установите из приватного репозитория:

```bash
pip install "pricezaim-sdk @ git+https://github.com/horatiiwork-design/pricezaim-sdk-python.git"
```

Для приватного GitHub-репозитория нужен токен с доступом к репозиторию.

## Быстрый старт

```python
import os

from pricezaim_sdk import Client

client = Client(os.environ["PRICEZAIM_API_KEY"])

page = client.auctions.list(status="active", per_page=20)

for auction in page:
    print(auction["id"], auction["title"])

print("Всего:", page.total)
```

Клиент можно использовать как context manager:

```python
with Client(os.environ["PRICEZAIM_API_KEY"]) as client:
    auctions = client.auctions.list()
```

## DTO

```python
from pricezaim_sdk import Auction

auction: Auction = client.auctions.get_dto(991)

print(auction.id)
print(auction.required_amount)
print(auction.client_profile.inn if auction.client_profile else None)

page = client.auctions.list_dto()
for item in page:
    assert isinstance(item, Auction)
```

Доступны:

- `Auction`
- `ClientProfile`
- `Bid`
- `Deal`
- `DealDocument`
- `Webhook`

DTO создаются через `from_dict()` и сохраняют исходные данные в `raw` / `to_dict()`.

## Аукционы

```python
created = client.auctions.create({
    "title": "Заявка №...",
    "city": "Москва",
    "required_amount": 500000,
})

client.auctions.start(created["id"])
client.auctions.stop(created["id"])
```

С файлами:

```python
from pricezaim_sdk import FileUpload

client.auctions.update(
    991,
    {"required_amount": 600000},
    [FileUpload("photos[]", "/tmp/photo.jpg")],
)
```

## Ставки

```python
client.bids.place(
    991,
    {"amount": 150000, "interest_rate": 19.5, "term": 24},
    idempotency_key="bid-991-1",
)
```

## Сделки

```python
deals = client.deals.list(status="active")
deal = client.deals.get(157)
client.deals.send_chat(157, "Документы отправлены.")
```

## Вебхуки

```python
from pricezaim_sdk import WebhookEvent, WebhookEventType, verify_request

raw_body = request.get_data()  # сырое тело, не json.dumps повторно
headers = request.headers

if not verify_request(raw_body, os.environ["PRICEZAIM_WEBHOOK_SECRET"], headers):
    raise PermissionError("Invalid webhook signature")

event = WebhookEvent.from_json(raw_body)

if event.type is WebhookEventType.AUCTION_STARTED:
    auction_id = event.auction_id
    # ...
```

`WebhookEvent` даёт:

- `event_id` — для дедупликации;
- `name` — имя события;
- `type` — `WebhookEventType | None`;
- `is_known` — известно ли событие;
- `auction_id` — id аукциона, если есть;
- `payload` / `to_dict()` — весь конверт.

Неизвестное событие нужно логировать и отвечать `200`, а не `400`.

## Автоповторы

По умолчанию выключены:

```bash
export PRICEZAIM_SDK_RETRIES_ENABLED=1
export PRICEZAIM_SDK_RETRY_ATTEMPTS=3
export PRICEZAIM_SDK_RETRY_BASE_DELAY_MS=200
```

Повторяются:

- `429`, `500`, `502`, `503`, `504`;
- сетевые ошибки и таймауты;
- `GET`, `HEAD`, `PUT`, `DELETE`, `OPTIONS`;
- `POST`/`PATCH` только с `idempotency_key`.

Не повторяются `400`, `401`, `403`, `404`, `422`.

При `429` учитывается `Retry-After`.

## Ошибки

```python
from pricezaim_sdk import ApiError, ValidationError

try:
    client.auctions.get(999999)
except ValidationError as exc:
    print(exc.errors)
except ApiError as exc:
    print(exc.status, exc.error_code, exc.request_id, exc.retry_after)
```

`TransportError` — сеть, DNS, таймаут, TLS.

## Документация

Подробный справочник по методам: [`docs/api.md`](docs/api.md).
