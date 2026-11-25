
import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo
)
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

if not TOKEN or not WEBAPP_URL:
    raise RuntimeError("Проверь BOT_TOKEN и WEBAPP_URL в .env")

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 ОТКРЫТЬ CRYPROGAMMA",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ]
        ]
    )

    await message.answer(
        "🟢 CRYPROGAMMA\n\n"
        "Привет! Добро пожаловать в CRYPROGAMMA — "
        "твой цифровой криптокошелёк!\n\n"
        "✨ Премиальный интерфейс\n"
        "💎 Управление цифровыми активами\n"
        "📊 Удобная панель платформы\n\n"
        "Нажми кнопку ниже, чтобы открыть приложение 👇",
        reply_markup=keyboard
    )


async def main():
    print("CRYPROGAMMA BOT запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
