import asyncio
from datetime import datetime, timezone

import httpx
import yfinance as yf

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"


async def get_ray_price() -> dict:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                COINGECKO_URL,
                params={"ids": "raydium", "vs_currencies": "usd"},
            )
            resp.raise_for_status()
            data = resp.json()
            price = data["raydium"]["usd"]
            return {"usd": price, "symbol": "RAY", "timestamp": ts}
    except Exception as e:
        return {"usd": None, "symbol": "RAY", "timestamp": ts, "error": str(e)}


def _fetch_pep_sync() -> float | None:
    ticker = yf.Ticker("PEP")
    price = ticker.fast_info.get("last_price")
    return float(price) if price is not None else None


async def get_pep_price() -> dict:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    try:
        loop = asyncio.get_event_loop()
        price = await loop.run_in_executor(None, _fetch_pep_sync)
        if price is None:
            return {"usd": None, "symbol": "PEP", "timestamp": ts, "error": "No data"}
        return {"usd": price, "symbol": "PEP", "timestamp": ts}
    except Exception as e:
        return {"usd": None, "symbol": "PEP", "timestamp": ts, "error": str(e)}
