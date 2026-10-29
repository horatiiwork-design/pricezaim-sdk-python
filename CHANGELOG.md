# Changelog

## 0.1.0 — 2026-10-29

- Первый Python SDK для публичного API pricezaim.
- Клиент на `httpx`, `X-API-Key`, JSON и multipart.
- Ресурсы `auctions`, `bids`, `deals`, `webhooks`.
- DTO: `Auction`, `ClientProfile`, `Bid`, `Deal`, `DealDocument`, `Webhook`.
- Пагинация и проверка подписи вебхуков.
- Opt-in автоповторы через env.
