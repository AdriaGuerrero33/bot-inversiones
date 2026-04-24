from datetime import datetime

import pytz
from telegram import Bot
from telegram.ext import Application

from prices import get_pep_price, get_ray_price


def build_application(token: str) -> Application:
    return Application.builder().token(token).build()


def _format_price(value: float | None, decimals: int) -> str:
    if value is None:
        return "N/A"
    return f"${value:,.{decimals}f}"


async def send_daily_price(bot: Bot, chat_id: str) -> None:
    ray = await get_ray_price()
    pep = await get_pep_price()

    madrid = pytz.timezone("Europe/Madrid")
    now = datetime.now(madrid).strftime("%d %b %Y, %H:%M")

    ray_price = _format_price(ray.get("usd"), 4)
    pep_price = _format_price(pep.get("usd"), 2)

    text = (
        f"📊 <b>Daily Price Update</b> — {now}\n\n"
        f"🟣 <b>RAY</b> (Raydium · Solana):  <code>{ray_price}</code>\n"
        f"🔵 <b>PEP</b> (PepsiCo · NASDAQ): <code>{pep_price}</code>"
    )

    if ray.get("error"):
        text += f"\n\n⚠️ RAY error: {ray['error']}"
    if pep.get("error"):
        text += f"\n⚠️ PEP error: {pep['error']}"

    await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
