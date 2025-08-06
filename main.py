import os
import time
import logging
import asyncio
import httpx
import sqlite3
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot
from telegram.error import TelegramError
from logging_config import setup_logging

# Constants
BYBIT_INSTRUMENTS_URL = "https://api.bybit.com/v5/market/instruments-info?category=spot"
DB_PATH = "symbols.db"
TABLE_NAME = "known_symbols"

# Load env vars
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
setup_logging()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

logger = logging.getLogger(__name__)

# Telegram setup
bot = Bot(token=TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else None

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        symbol TEXT PRIMARY KEY,
        market_type TEXT,
        status TEXT,
        create_time_utc TEXT
    )
    """)
    conn.commit()
    conn.close()


def fetch_existing_symbols():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(f"SELECT symbol FROM {TABLE_NAME}")
    data = {row[0] for row in c.fetchall()}
    conn.close()
    return data

def add_symbol_to_db(symbol, market_type, status, create_time_utc):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(f"""
        INSERT OR IGNORE INTO {TABLE_NAME} (symbol, market_type, status, create_time_utc)
        VALUES (?, ?, ?, ?)
    """, (symbol, market_type, status, create_time_utc))
    conn.commit()
    conn.close()

async def fetch_bybit_instruments():
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.get(BYBIT_INSTRUMENTS_URL)
            r.raise_for_status()
            data = r.json()
            if "result" not in data or "list" not in data["result"]:
                raise ValueError("Unexpected API structure: {}".format(data))
            return data["result"]["list"]
        except Exception as e:
            logger.error(f"Error fetching Bybit instruments: {e}")
            return None

def format_notify(symbol_info):
    s = symbol_info
    msg = (
        f"\u2728 New listing: <b>{s.get('symbol')}</b>\n"
        f"Type: {s.get('market')} | Status: {s.get('status')}\n"
    )
    created_time = s.get('created_time')
    if created_time:
        msg += f"Listed at: {created_time[:19].replace('T', ' ')} UTC"
    else:
        msg += "Listed at: время неизвестно"
    return msg

async def send_telegram_notification(message):
    if not bot or not TELEGRAM_CHAT_ID:
        logger.error("Telegram bot token or chat ID not configured.")
        return
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="HTML")
        logger.info(f"Notification sent: {message}")
    except TelegramError as e:
        logger.error(f"Failed to send Telegram notification: {e}")

def symbol_extract(s):
    return {
        'symbol': s.get('symbol'),
        'market': s.get('baseCoin'),
        'status': s.get('status'),
        'created_time': s.get('createdTime')
    }

# Main bot logic
async def monitor_new_listings():
    logger.info("Bot started. Monitoring for new listings...")
    existing = fetch_existing_symbols()
    seen = set(existing)
    while True:
        symbols = await fetch_bybit_instruments()
        if not symbols:
            await asyncio.sleep(9)
            continue
        current_set = set(s.get('symbol') for s in symbols)
        new_listings = [s for s in symbols if s.get('symbol') not in seen]
        for symbol in new_listings:
            info = {
                'symbol': symbol.get('symbol'),
                'market': symbol.get('baseCoin'),
                'status': symbol.get('status'),
                'created_time': symbol.get('createdTime')
            }
            msg = format_notify(info)
            asyncio.create_task(send_telegram_notification(msg))
            add_symbol_to_db(info['symbol'], info['market'], info['status'], info['created_time'])
            seen.add(info['symbol'])
        await asyncio.sleep(7)

if __name__ == "__main__":
    init_db()
    try:
        asyncio.run(monitor_new_listings())
    except KeyboardInterrupt:
        print("Bot stopped by user.")
