import asyncio
import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import BOT_TOKEN
import database as db
from handlers import user, admin


logging.basicConfig(level=logging.INFO)


async def health(request):
    """Render/UptimeRobot shu manzilga so'rov yuborib, botni 'uyg'oq' tutadi"""
    return web.Response(text="Bot ishlayapti ✅")


async def start_web_server():
    """Render.com 'Web Service' bo'lgani uchun biror portni tinglash shart"""
    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Web server {port}-portda ishga tushdi")


async def eslatmalarni_yuborish(bot: Bot):
    """Ertaga muddati tugaydigan bandlar uchun mijozga eslatma yuboradi"""
    bandlar = await db.get_bookings_ending_tomorrow()
    for b in bandlar:
        try:
            await bot.send_message(
                b["telegram_id"],
                f"🔔 <b>Eslatma!</b>\n\n"
                f"🥼 №{b['raqam']} xalatni ertaga ({b['tugash_sana']}) "
                f"qaytarish muddati tugaydi.\n"
                f"Iltimos, o'z vaqtida qaytaring yoki muddatni uzaytiring.",
            )
        except Exception:
            pass
        await db.mark_eslatma_yuborildi(b["id"])


async def main():
    await db.init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_router(admin.router)
    dp.include_router(user.router)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(eslatmalarni_yuborish, "cron", hour=9, minute=0, args=[bot])
    scheduler.start()

    await bot.delete_webhook(drop_pending_updates=True)
    await start_web_server()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
