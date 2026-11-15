import asyncio
import os
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, WebAppData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import json

BOT_TOKEN = os.environ.get("BOT_TOKEN", "ТВОЙ_ТОКЕН")
ADMIN_IDS = [8636027393]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ПРОСТАЯ БАЗА (Сбрасывается при перезапуске Render)
users = {}
def get_user(uid):
    if uid not in users:
        users[uid] = {"balance": 0.0, "banned": False}
    return users[uid]

def is_admin(uid): return uid in ADMIN_IDS

class UserStates(StatesGroup):
    waiting_deposit_amount = State()

def main_menu(uid):
    WEBAPP_URL = "cryptoapp-67-5eomgmwkq-crypto-gamma-bot.vercel.app" # ТВОЯ ССЫЛКА
    
    kb = [
        [InlineKeyboardButton(text="🚀 Открыть Mini App", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton(text="💰 Мой баланс", callback_data="balance")],
    ]
    if is_admin(uid):
        kb.append([InlineKeyboardButton(text="👑 Админка", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

@dp.message(Command("start"))
async def start(message: Message):
    uid = message.from_user.id
    get_user(uid)
    await message.answer("👋 **Добро пожаловать в CryptoGamma!**\n\nВыбери действие:", reply_markup=main_menu(uid), parse_mode="Markdown")

@dp.callback_query(F.data == "balance")
async def show_balance(call: CallbackQuery):
    user = get_user(call.from_user.id)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]])
    await call.message.edit_text(f"💰 Баланс: `{user['balance']:.4f}` USDT", reply_markup=kb, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(F.data == "back")
async def back(call: CallbackQuery):
    await call.message.edit_text("👋 Главное меню", reply_markup=main_menu(call.from_user.id))

# ==================== ЛОВИМ ДАННЫЕ ИЗ MINI APP ====================
@dp.message(F.web_app_data)
async def web_app_handler(message: Message):
    try:
        data = json.loads(message.web_app_data.data)
        action = data.get("action")
        uid = message.from_user.id

        # Пополнение
        if action == "deposit":
            await message.answer("📥 Чтобы пополнить, введи сумму в чат (пока заглушка):")
            # Здесь можно добавить FSM для ввода суммы
            
        # Участие в розыгрыше
        elif action == "join_giveaway":
            await message.answer("🎉 Ты успешно участвуешь в розыгрыше 100 USDT! Удачи!")
            
        # Админ: Выдать баланс
        elif action == "add_balance" and is_admin(uid):
            target_id = int(data.get("target_id"))
            amount = float(data.get("amount"))
            target_user = get_user(target_id)
            target_user["balance"] += amount
            await message.answer(f"✅ Выдано {amount} USDT пользователю {target_id}.\nЕго новый баланс: {target_user['balance']:.2f} USDT")
            try:
                await bot.send_message(target_id, f"🎁 Вам начислено {amount} USDT от администратора!")
            except:
                pass

        # Админ: Розыгрыш
        elif action == "start_giveaway" and is_admin(uid):
            text = data.get("text")
            sent = 0
            for u in users.keys():
                try:
                    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🎉 Участвовать", web_app=WebAppInfo(url="https://cryptoapp3.vercel.app"))]])
                    await bot.send_message(u, f"🎁 **РОЗЫГРЫШ!**\n\n{text}\n\nНажми кнопку ниже, чтобы участвовать!", reply_markup=kb, parse_mode="Markdown")
                    sent += 1
                except:
                    pass
            await message.answer(f"✅ Розыгрыш разослан {sent} пользователям!")

    except Exception as e:
        await message.answer(f"❌ Ошибка обработки данных: {e}")

# ==================== ВЕБ-СЕРВЕР ДЛЯ RENDER ====================
async def handle(request):
    return web.Response(text="CryptoGamma is alive!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    print("CryptoGamma запущен на Render!")
    await start_web_server() 
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
