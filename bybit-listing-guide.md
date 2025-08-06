# Bybit New Listing Instant Notification Bot — Step-by-Step Implementation Guide

## 1. Bybit API Features & Analysis

### API Structure
- **REST API:** Unified V5 endpoints, including `/v5/market/instruments-info` for all trading pairs.
- **WebSocket API:** Offers public streams per market (Spot, Derivatives, etc.), topics include `orderbook`, `ticker`, `trade`, and per-symbol `instrument_info.<SYMBOL>`. Allows real-time market data.
- **Update Frequency:** REST updates reflect within 1 minute of listing; WebSocket topics push real-time changes.
- **Rate Limits:**
  - **REST:** Max 75 requests/second per IP (per docs). Spot endpoint returns all instruments at once and does not paginate.
  - **WebSocket:** Connection: 500/5min/IP. Heartbeat required every ~20 seconds.

### Instrument Discovery & Tracking
- **REST:** Regular polling of `/v5/market/instruments-info?category=spot` returns all pairs, but delay is up to polling interval.
- **WebSocket:** Instant push for listing/delisting—if listening to right topic. However, WebSocket does *not* have a global "all instruments" topic, only per-symbol subscriptions (per V5 public docs and real-world usage in open-source SDKs).

### Conclusion: REST polling is the only universal and scalable method. WebSocket is primarily optimized for real-time price data, not universal new-symbol push.


## 2. Detecting New Listings in Real Time

- **Best Practice**: Periodically poll the REST `/v5/market/instruments-info?category=spot` endpoint.
- Maintain a persistent cache (in database, file, or in-memory) of previously observed symbols.
- Compare results from each fetch to find newly listed pairs.
- For lowest latency: poll REST every 5–10 seconds (within rate limits; can go even lower but beware of possible IP ban if rate-limited).
- Capture listing timestamp at the moment the pair is first seen in API response.

- **Alternative:** Also monitor Bybit’s official announcement feed for redundancy, but API is the source of truth and is always fastest.


## 3. Optimal Python Libraries

### For Exchange Monitoring:
- `requests` or `httpx` — simple REST polling, httpx for async/concurrency if scaling up.
- `schedule` or `APScheduler` — reliable frequent task scheduling.
- `json`, `time`, `asyncio` — built-in modules.
- `python-dotenv` — for secrets/config management.

### For Telegram Push:
- `python-telegram-bot` — battle-tested, full-featured library. Supports bot notification to channels/groups/users.
- Alternatives: `aiogram` (async/modern), or direct HTTPS requests to Telegram Bot API.

### For Robustness:
- `tenacity` — retries for network errors.
- `sqlite` or `TinyDB` — lightweight on-disk persistence (optional but improves reliability across restarts).


## 4. Delay-Minimizing Monitoring Algorithm

- On startup: fetch and cache the full list of `symbol` (pairs).
- Set a recurring async task (e.g. with APScheduler or asyncio loop).
- Every 5–10 seconds:
  - Fetch `instruments-info`.
  - Compare currently returned symbols with the cache.
  - If new symbols found:
    - Grab meta fields: market type, status, and if available, creation time.
    - Send formatted Telegram notification: SYMBOL, creation timestamp (in UTC), all relevant details.
  - Update local cache.
- Use retries and error handling for API/network issues.
- Track previously notified symbols to avoid duplicate alerts on restart (persistence recommended).

- **Notification Format:**
  - `New listing: <symbol> — Listed at: <timestamp>`


## 5. Solution Architecture Diagram

[The following diagram will be saved as a separate file and referenced.]


## 6. Recommendations: Stability, Scalability, Extensibility

- Always persist known symbol list (file or DB) in case bot restarts.
- Add logging, error reporting, and Telegram error notification for robustness.
- Use async REST polling (`httpx`, `asyncio`) for future scalability and multi-exchange support.
- Abstract API interface: make REST polling and symbol diff logic modular so code can be adapted for Binance, Kucoin, etc.
- Do not exceed rate limits—use backoff and adaptive polling if any rate-limit error is seen.
- Optionally: run multiple bots for different market types (spot, derivatives) by varying the `category` param.
- Secure all credentials (use env vars, `.env`, or cloud secret managers if deploying at scale).


## 7. References / Further Reading
- [Bybit V5 API Docs](https://bybit-exchange.github.io/docs/v5/market/instrument)
- [Official Bybit Python SDK (pybit)](https://github.com/bybit-exchange/pybit)
- [Telegram Bot API Docs](https://core.telegram.org/bots/api)


---

**Next:** A separate file (diagram.png) will be provided to visually illustrate the solution architecture as described above.