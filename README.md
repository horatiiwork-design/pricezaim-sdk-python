# pricezaim Python SDK

Python-клиент публичного API [pricezaim](https://api.pricezaim.ru/docs).
Синхронный, на `httpx`, с типами, DTO и проверкой подписи вебхуков.

Требуется Python 3.10+.

## Установка

После публикации в PyPI:

```bash
pip install pricezaim-sdk
```

До публикации:

```bash
pip install "pricezaim-sdk @ git+https://github.com/horatiiwork-design/pricezaim-sdk-python.git"
```

Для приватного GitHub-репозитория нужен токен с доступом к нему.

## Начало работы

```python
import os

from pricezaim_sdk import Client

client = Client(os.environ["PRICEZAIM_API_KEY"])

page = client.auctions.list(status="active", per_page=20)

for auction in page:
    print(auction["id"], auction["title"])

print("Всего:", page.total)
```

Клиент можно закрывать явно или использовать как context manager:

```python
with Client(os.environ["PRICEZAIM_API_KEY"]) as client:
    auctions = client.auctions.list()
```

Параметры клиента:

```python
Client(
    api_key,
    base_url="https://api.pricezaim.ru",
    timeout=15.0,
    http_client=None,  # свой httpx.Client, если нужен прокси или тесты
)
```

Если API развёрнут под префиксом пути, укажите его в `base_url`: SDK
добавляет только `/v1/...`.

## Ресурсы

| Ресурс | Что делает |
|---|---|
| `client.auctions` | список, карточка, создание, изменение, запуск, архивация, победитель, отказ, фото и файлы |
| `client.bids` | свои ставки, ставки аукциона, размещение ставки |
| `client.deals` | список, карточка, документы, реквизиты, согласование, чат |
| `client.webhooks` | создание, изменение, удаление, тестовая доставка, журнал и повтор доставки |

Методы с суффиксом `_dto` возвращают dataclasses:

```python
from pricezaim_sdk import Auction

auction = client.auctions.get_dto(991)

if isinstance(auction, Auction):
    print(auction.required_amount)
    print(auction.client_profile.inn if auction.client_profile else None)
```

DTO переживают неполный ответ: отсутствующие поля будут `None` или пустыми
коллекциями. Исходный словарь доступен в `to_dict()`.

## Вебхуки

Подпись считается по сырому телу. Если пересобрать JSON, подпись не сойдётся.

```python
import os

from pricezaim_sdk import WebhookEvent, WebhookEventType, verify_request

raw_body = request.body  # bytes, тело запроса из вашего фреймворка
headers = request.headers

if not verify_request(raw_body, os.environ["PRICEZAIM_WEBHOOK_SECRET"], headers):
    raise PermissionError("Invalid webhook signature")

event = WebhookEvent.from_json(raw_body)

if event.type is WebhookEventType.AUCTION_STARTED:
    auction_id = event.auction_id
    # ...
```

`WebhookEvent` отдаёт `event_id`, `name`, `type`, `is_known`, `auction_id` и
`payload`. Неизвестное событие нужно залогировать и ответить `200`, чтобы новые
события на платформе не ломали приёмник.

## Повторы запросов

По умолчанию выключены:

```bash
export PRICEZAIM_SDK_RETRIES_ENABLED=1
export PRICEZAIM_SDK_RETRY_ATTEMPTS=3
export PRICEZAIM_SDK_RETRY_BASE_DELAY_MS=200
```

Повторяются `429`, `500`, `502`, `503`, `504` и сетевые ошибки. `GET`, `HEAD`,
`PUT`, `DELETE`, `OPTIONS` повторяются всегда; `POST` и `PATCH` — только с
`idempotency_key`. Ответы `400`, `401`, `403`, `404`, `422` не повторяются.
`Retry-After` учитывается.

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

`TransportError` выбрасывается при сетевой ошибке, таймауте или TLS.

## Разработка

```bash
python -m pytest
ruff check src tests
mypy src
python -m build
```

Справочник по методам и типам — в [`docs/api.md`](docs/api.md).
