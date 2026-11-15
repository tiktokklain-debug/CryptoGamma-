import asyncio
import os
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Токен берется из настроек Render (Environment Variables)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "ТВОЙ_ТОКЕН_СЮДА")
ADMIN_IDS = [8636027393]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

users = {}
def get_user(uid):
    if uid not in users:
        users[uid] = {"balance": {"USDT": 0.0}, "banned": False, "username": "", "agreed": False}
    return users[uid]

def is_admin(uid): return uid in ADMIN_IDS

class UserStates(StatesGroup):
    waiting_deposit_amount = State()
    waiting_withdraw_amount = State()

class AdminStates(StatesGroup):
    waiting_broadcast = State()

def main_menu(uid):
    # Кнопка Mini App (пока ведет на заглушку, потом заменишь на свою ссылку с Vercel)
    web_app_url = "cryptoapp-1-if4v8etmq-crypto-gamma-bot.vercel.app" 
    
    kb = [
        [InlineKeyboardButton(text="🚀 Открыть Mini App", web_app=WebAppInfo(url=web_app_url))],
        [InlineKeyboardButton(text="💰 Мой баланс", callback_data="balance"),
         InlineKeyboardButton(text="📥 Пополнить", callback_data="deposit_menu")],
        [InlineKeyboardButton(text="💸 Вывод", callback_data="withdraw_menu")],
        [InlineKeyboardButton(text="📜 Оферта", callback_data="offer")],
    ]
    if is_admin(uid):
        kb.append([InlineKeyboardButton(text="👑 Админка", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

async def safe_edit(call: CallbackQuery, text: str, kb: InlineKeyboardMarkup = None):
    try:
        if call.message.photo:
            await call.message.edit_caption(caption=text, reply_markup=kb, parse_mode="Markdown")
        else:
            await call.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    except:
        await call.message.answer(text, reply_markup=kb, parse_mode="Markdown")

@dp.message(Command("start"))
async def start(message: Message):
    uid = message.from_user.id
    get_user(uid)
    users[uid]["username"] = message.from_user.username or ""
    if users[uid].get("banned"):
        return await message.answer("🚫 Вы забанены.")
    await message.answer("👋 **Добро пожаловать в CryptoGamma!**\n\nВыбери действие:", reply_markup=main_menu(uid), parse_mode="Markdown")

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(call: CallbackQuery):
    await safe_edit(call, "👋 **Главное меню**", main_menu(call.from_user.id))
    await call.answer()

@dp.callback_query(F.data == "balance")
async def show_balance(call: CallbackQuery):
    user = get_user(call.from_user.id)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]])
    await safe_edit(call, f"💰 Баланс: `{user['balance']['USDT']:.4f}` USDT", kb)
    await call.answer()

@dp.callback_query(F.data == "offer")
async def show_offer(call: CallbackQuery):
    text = "📜 **Оферта**\n\n1. Сервис внутренний.\n2. Вывод в разработке.\n3. Вы соглашаетесь с рисками."
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Принимаю", callback_data="accept_offer")], [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]])
    await safe_edit(call, text, kb)
    await call.answer()

@dp.callback_query(F.data == "accept_offer")
async def accept_offer(call: CallbackQuery):
    get_user(call.from_user.id)["agreed"] = True
    await call.answer("✅ Оферта принята!", show_alert=True)
    await back_to_menu(call)

@dp.callback_query(F.data == "deposit_menu")
async def deposit_menu(call: CallbackQuery):
    if not get_user(call.from_user.id).get("agreed"):
        await call.answer("⚠️ Сначала примите Оферту!", show_alert=True)
        return await show_offer(call)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💵 Ввести сумму", callback_data="dep_custom")], [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]])
    await safe_edit(call, "📥 **Пополнение**", kb)
    await call.answer()

@dp.callback_query(F.data == "dep_custom")
async def dep_custom(call: CallbackQuery, state: FSMContext):
    await state.set_state(UserStates.waiting_deposit_amount)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_menu")]])
    await safe_edit(call, "✍️ Введи сумму в чат:", kb)
    await call.answer()

@dp.message(UserStates.waiting_deposit_amount)
async def process_deposit(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount <= 0: raise ValueError
    except:
        return await message.answer("❌ Введи число.")
    await state.clear()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_menu")]])
    await message.answer(f"✅ Введено {amount} USDT (Заглушка API)", reply_markup=kb)

@dp.callback_query(F.data == "withdraw_menu")
async def withdraw_menu(call: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]])
    await safe_edit(call, "💸 **Вывод в разработке**", kb)
    await call.answer()

@dp.callback_query(F.data == "admin_panel")
async def admin_panel(call: CallbackQuery):
    if not is_admin(call.from_user.id): return await call.answer("Нет доступа", show_alert=True)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]])
    await safe_edit(call, "👑 **Админка (упрощенная)**", kb)
    await call.answer()

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
