# Справочник методов Python SDK

Все ресурсы доступны через `Client`:

```python
from pricezaim_sdk import Client

client = Client(api_key)
```

## Client

| Метод | Возвращает | Назначение |
|---|---|---|
| `auctions` | `Auctions` | Ресурс аукционов |
| `bids` | `Bids` | Ресурс ставок |
| `deals` | `Deals` | Ресурс сделок |
| `webhooks` | `Webhooks` | Ресурс вебхуков |
| `get(path, params=...)` | `dict` | GET-запрос |
| `post(path, payload=..., idempotency_key=...)` | `dict` | POST с JSON |
| `post_multipart(path, data=..., files=...)` | `dict` | POST multipart |
| `put(path, payload)` | `dict` | PUT с JSON |
| `put_multipart(path, data=..., files=...)` | `dict` | PUT multipart |
| `delete(path)` | `dict` | DELETE |
| `send(...)` | `dict` | Запрос + JSON-декодирование |
| `send_raw(method, path, params=...)` | `httpx.Response` | Сырой ответ для файлов |
| `request(...)` | `httpx.Response` | HTTP-запрос с повторами |
| `retry_policy` | `RetryPolicy` | Текущая политика повторов |
| `close()` | `None` | Закрыть собственный HTTP-клиент |

## Аукционы

```python
client.auctions
```

| Метод | HTTP | Возвращает | Назначение |
|---|---|---|---|
| `list(**filters)` | `GET /v1/auctions` | `Page[dict]` | Доступные аукционы |
| `my(**filters)` | `GET /v1/auctions/my` | `Page[dict]` | Аукционы организации |
| `list_dto(**filters)` | `GET /v1/auctions` | `Page[Auction]` | С DTO |
| `my_dto(**filters)` | `GET /v1/auctions/my` | `Page[Auction]` | С DTO |
| `get(auction_id)` | `GET /v1/auctions/{id}` | `dict` | Карточка |
| `get_dto(auction_id)` | `GET /v1/auctions/{id}` | `Auction` | Карточка как DTO |
| `create(payload, files=...)` | `POST /v1/auctions` | `dict` | Создать draft |
| `create_dto(payload, files=...)` | `POST /v1/auctions` | `Auction` | Создать и вернуть DTO |
| `update(id, payload, files=...)` | `PUT /v1/auctions/{id}` | `dict` | Изменить |
| `update_dto(id, payload, files=...)` | `PUT /v1/auctions/{id}` | `Auction` | Изменить и вернуть DTO |
| `start(id)` | `POST /v1/auctions/{id}/start` | `dict` | Запустить |
| `stop(id)` | `POST /v1/auctions/{id}/stop` | `dict` | Архивировать |
| `select_winner(id, bid_id)` | `POST /v1/auctions/{id}/winner` | `dict` | Выбрать победителя |
| `duplicate(id)` | `POST /v1/auctions/{id}/duplicate` | `dict` | Пометить дублем |
| `restore_duplicate(id)` | `DELETE /v1/auctions/{id}/duplicate` | `dict` | Снять пометку |
| `refuse(id, payload)` | `POST /v1/auctions/{id}/refusal` | `dict` | Отказаться |
| `restore_refusal(id)` | `DELETE /v1/auctions/{id}/refusal` | `dict` | Снять отказ |
| `photos(id)` | `GET /v1/auctions/{id}/photos` | `dict` | Фото и файлы |
| `download_file(id, file_id)` | `GET /v1/auctions/{id}/files/{file_id}` | `bytes` | Скачать файл |

Файлы:

```python
from pricezaim_sdk import FileUpload

FileUpload("photos[]", "/tmp/photo.jpg", "photo.jpg")
```

## Ставки

```python
client.bids
```

| Метод | HTTP | Возвращает | Назначение |
|---|---|---|---|
| `my(**filters)` | `GET /v1/bids/my` | `Page[dict]` | Свои ставки |
| `my_dto(**filters)` | `GET /v1/bids/my` | `Page[Bid]` | С DTO |
| `for_auction(auction_id, **filters)` | `GET /v1/auctions/{id}/bids` | `Page[dict]` | Ставки аукциона |
| `for_auction_dto(auction_id, **filters)` | `GET /v1/auctions/{id}/bids` | `Page[Bid]` | С DTO |
| `place(auction_id, payload, idempotency_key=...)` | `POST /v1/auctions/{id}/bids` | `dict` | Поставить ставку |
| `place_dto(...)` | `POST /v1/auctions/{id}/bids` | `Bid` | Ставка как DTO |

`payload`: `amount`, `interest_rate`, `term`, `comment`.

## Сделки

```python
client.deals
```

| Метод | HTTP | Возвращает | Назначение |
|---|---|---|---|
| `list(**filters)` | `GET /v1/deals` | `Page[dict]` | Список сделок |
| `list_dto(**filters)` | `GET /v1/deals` | `Page[Deal]` | С DTO |
| `get(deal_id)` | `GET /v1/deals/{id}` | `dict` | Карточка |
| `get_dto(deal_id)` | `GET /v1/deals/{id}` | `Deal` | Карточка как DTO |
| `documents(deal_id)` | `GET /v1/deals/{id}/documents` | `dict` | Документы |
| `documents_dto(deal_id)` | `GET /v1/deals/{id}/documents` | `list[DealDocument]` | Документы как DTO |
| `upload_documents(id, files, fields=..., idempotency_key=...)` | `POST /v1/deals/{id}/documents` | `dict` | Загрузить |
| `requisites(deal_id)` | `GET /v1/deals/{id}/requisites` | `dict` | Реквизиты |
| `approve(deal_id, payload=..., idempotency_key=...)` | `POST /v1/deals/{id}/approve` | `dict` | Согласовать |
| `chat(deal_id, **filters)` | `GET /v1/deals/{id}/chat` | `dict` | История чата |
| `send_chat(deal_id, message, payload=..., idempotency_key=...)` | `POST /v1/deals/{id}/chat` | `dict` | Сообщение |
| `download_document(deal_id, document_id)` | `GET /v1/deals/{id}/documents/{doc_id}` | `bytes` | Скачать |
| `delete_document(deal_id, document_id)` | `DELETE /v1/deals/{id}/documents/{doc_id}` | `dict` | Удалить |

## Вебхуки

```python
client.webhooks
```

| Метод | HTTP | Возвращает | Назначение |
|---|---|---|---|
| `list()` | `GET /v1/webhooks` | `dict` | Список без секретов |
| `list_dto()` | `GET /v1/webhooks` | `list[Webhook]` | С DTO |
| `create(payload, idempotency_key=...)` | `POST /v1/webhooks` | `dict` | Создать |
| `create_dto(...)` | `POST /v1/webhooks` | `Webhook` | Создать и вернуть DTO |
| `update(id, payload)` | `PUT /v1/webhooks/{id}` | `dict` | Изменить |
| `update_dto(id, payload)` | `PUT /v1/webhooks/{id}` | `Webhook` | Изменить и вернуть DTO |
| `delete(id)` | `DELETE /v1/webhooks/{id}` | `dict` | Удалить |
| `test(id)` | `POST /v1/webhooks/{id}/test` | `dict` | Тестовый пинг |
| `deliveries(id, **filters)` | `GET /v1/webhooks/{id}/deliveries` | `Page[dict]` | Журнал |
| `retry_delivery(webhook_id, delivery_id)` | `POST /v1/webhooks/{id}/deliveries/{delivery_id}/retry` | `dict` | Повторить |

## Page

`Page[T]` поддерживает `len()`, `iter()`, индексацию и `map()`.

| Свойство / метод | Возвращает | Назначение |
|---|---|---|
| `items` | `list[T]` | Элементы |
| `data` | `list[T]` | Псевдоним `items` |
| `meta` | `dict` | Метаданные |
| `raw` | `dict` | Исходный ответ |
| `total` | `int` | Всего записей |
| `current_page` | `int` | Текущая страница |
| `last_page` | `int` | Последняя страница |
| `per_page` | `int` | Размер страницы |
| `is_empty()` | `bool` | Пуста ли страница |
| `map(fn)` | `Page[U]` | Преобразовать элементы |

## DTO

| DTO | Основные поля |
|---|---|
| `Auction` | `id`, `status`, `required_amount`, `can_bid`, `client_profile` |
| `ClientProfile` | `inn`, `passport_number`, `income_salary`; содержит ПДн |
| `Bid` | `id`, `auction_id`, `amount`, `interest_rate`, `term` |
| `Deal` | `id`, `status`, `documents`, `document_objects()` |
| `DealDocument` | `id`, `original_name`, `mime`, `size` |
| `Webhook` | `id`, `url`, `events`, `active`, `has_secret` |

Все DTO имеют `from_dict()` и `to_dict()`.

## Вебхуки

| Функция | Возвращает | Назначение |
|---|---|---|
| `verify(payload, secret, signature, timestamp=None, tolerance=300)` | `bool` | Проверить HMAC |
| `verify_request(payload, secret, headers, tolerance=300)` | `bool` | Проверить по заголовкам |
| `sign(payload, secret)` | `str` | Посчитать HMAC-SHA256 |

`WebhookEvent`:

| Свойство / метод | Возвращает | Назначение |
|---|---|---|
| `from_json(raw)` | `WebhookEvent` | Разобрать тело |
| `from_dict(payload)` | `WebhookEvent` | Разобрать словарь |
| `event_id` | `str` | ID события |
| `name` | `str` | Имя события |
| `type` | `WebhookEventType \| None` | Известный тип |
| `is_known` | `bool` | Известно ли событие |
| `auction_id` | `int \| None` | ID аукциона |
| `payload` | `dict` | Полный конверт |
| `is_(event_type)` | `bool` | Сравнить тип |

`WebhookEventType` — enum известных событий, включая `AUCTION_STARTED`, `BID_OUTBID`, `DEAL_CREATED`, `WEBHOOK_TEST`.

## Автоповторы

| Условие | Повтор |
|---|---|
| env `PRICEZAIM_SDK_RETRIES_ENABLED=1` | Включены |
| `429`, `500`, `502`, `503`, `504` | Да |
| Сеть/таймаут | Да |
| `GET`, `HEAD`, `PUT`, `DELETE`, `OPTIONS` | Да |
| `POST`, `PATCH` без `idempotency_key` | Нет |
| `POST`, `PATCH` с `idempotency_key` | Да |
| `400`, `401`, `403`, `404`, `422` | Нет |

## Исключения

| Класс | Когда возникает |
|---|---|
| `ApiError` | HTTP `4xx/5xx` или не-JSON ответ |
| `ValidationError` | `422`, содержит `errors` |
| `TransportError` | Сеть, DNS, таймаут, TLS |
