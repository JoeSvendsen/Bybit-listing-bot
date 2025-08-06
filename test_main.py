import os
import sqlite3
import tempfile
import asyncio
import main
import pytest

TEST_SYMBOL = "TEST-DEF"

def test_db_persistence():
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    try:
        main.DB_PATH = db_path
        main.init_db()
        # Insert test symbol
        symbol = TEST_SYMBOL
        market_type = "SPOT"
        status = "Trading"
        create_time_utc = "2024-01-01T00:00:00Z"
        main.add_symbol_to_db(symbol, market_type, status, create_time_utc)
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(f"SELECT symbol, market_type, status, create_time_utc FROM {main.TABLE_NAME} WHERE symbol=?", (symbol,))
        data = cur.fetchone()
        conn.close()
        assert data == (symbol, market_type, status, create_time_utc)
    finally:
        os.close(db_fd)
        os.remove(db_path)

def test_format_notify():
    info = {
        'symbol': 'FOO-USDT',
        'market': 'FOO',
        'status': 'Trading',
        'created_time': '2024-01-01T00:00:00Z'
    }
    msg = main.format_notify(info)
    assert 'FOO-USDT' in msg
    assert 'Trading' in msg
    assert '2024-01-01' in msg

@pytest.mark.asyncio
async def test_fetch_bybit_instruments(monkeypatch):
    class FakeResponse:
        def json(self):
            return {"result": {"list": [{"symbol": "FOO-BAR", "baseCoin": "FOO", "status": "Trading", "createdTime": "2024-01-01T00:00:00Z"}]}}
        def raise_for_status(self):
            pass
    async def fake_get(*args, **kwargs):
        return FakeResponse()
    class Client:
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): return False
        async def get(self, *a, **kw): return await fake_get()
    monkeypatch.setattr(main.httpx, "AsyncClient", lambda *a, **kw: Client())
    res = await main.fetch_bybit_instruments()
    assert type(res) is list
    assert res and res[0]["symbol"] == "FOO-BAR"
