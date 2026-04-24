import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from bot import build_application, send_daily_price
from prices import get_pep_price, get_ray_price
from scheduler import build_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if token and chat_id:
        application = build_application(token)
        await application.initialize()
        await application.start()

        scheduler = build_scheduler(
            lambda: send_daily_price(application.bot, chat_id)
        )
        scheduler.start()

        app.state.bot_app = application
        app.state.scheduler = scheduler
    else:
        print("WARNING: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set — bot disabled")
        app.state.bot_app = None
        app.state.scheduler = None

    yield

    if app.state.bot_app:
        if app.state.scheduler:
            app.state.scheduler.shutdown(wait=False)
        await app.state.bot_app.stop()
        await app.state.bot_app.shutdown()


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    ray, pep = await get_ray_price(), await get_pep_price()
    return templates.TemplateResponse(
        "index.html", {"request": request, "ray": ray, "pep": pep}
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
