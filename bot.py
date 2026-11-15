import asyncio
import os
import aiohttp
import aiosqlite
import json
import qrcode
from io import BytesIO
from datetime import datetime
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, BufferedInputFile

# ==================== НАСТРОЙКИ ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "ТВОЙ_ТОКЕН")
ADMIN_IDS = [8636027393]
WEBAPP_URL = "https://cryptoapperroe.vercel.app"
XROCKET_PAY_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBJZCI6IjMwNzY4NiIsImp0aSI6ImFwcDozMDc2ODY6MTFhOTJmMDctNzY3ZS00MjIyLWJmZTEtNGViYTMzZDFlNGRjIiwiaWF0IjoxNzk0NzcyNDg0fQ.QMufXBwVwwKzEePsAjDzggAiosSwtlOiALEj85y_Q7I" # Вставь свой ключ из xRocket Pay
REF_BONUS = 0.05

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
DB_NAME = "database.db"

# ==================== БАЗА ДАННЫХ ====================
async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance REAL DEFAULT 0.0, is_banned INTEGER DEFAULT 0, referrer_id INTEGER DEFAULT NULL)")
        await db.execute("CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, type TEXT, amount REAL, date TEXT)")
        await db.commit()

async def get_user(uid):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (uid,)) as cursor:
            user = await cursor.fetchone()
            if not user:
                await db.execute("INSERT INTO users (user_id) VALUES (?)", (uid,))
                await db.commit()
                return {"user_id": uid, "balance": 0.0, "is_banned": 0, "referrer_id": None}
            return {"user_id": user[0], "balance": user[1], "is_banned": user[2], "referrer_id": user[3]}

async def update_balance(uid, amount, type_op="Бонус"):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, uid))
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        await db.execute("INSERT INTO history (user_id, type, amount, date) VALUES (?, ?, ?, ?)", (uid, type_op, amount, now))
        await db.commit()

async def get_history(uid):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT type, amount, date FROM history WHERE user_id = ? ORDER BY id DESC LIMIT 10", (uid,)) as cursor:
            return await cursor.fetchall()

# ==================== МЕНЮ ====================
@dp.message(Command("start"))
async def start(message: Message):
    uid = message.from_user.id
    args = message.text.split()
    user = await get_user(uid)
    
    if len(args) > 1 and args[1].isdigit():
        ref_id = int(args[1])
        if ref_id != uid and user["referrer_id"] is None:
            await get_user(ref_id)
            await update_balance(ref_id, REF_BONUS, "Реферальный бонус")
            async with aiosqlite.connect(DB_NAME) as db:
                await db.execute("UPDATE users SET referrer_id = ? WHERE user_id = ?", (ref_id, uid))
                await db.commit()
            try:
                await bot.send_message(ref_id, f"🎉 По твоей ссылке зашел друг! Тебе начислено {REF_BONUS} USDT.")
            except: pass

    await message.answer("👋 **Добро пожаловать в CryptoGamma!**", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🚀 Открыть Mini App", web_app=WebAppInfo(url=WEBAPP_URL))]]), parse_mode="Markdown")

# ==================== ОБРАБОТКА ДАННЫХ ====================
@dp.message(F.web_app_data)
async def web_app_handler(message: Message):
    try:
        data = json.loads(message.web_app_data.data)
        action = data.get("action")
        uid = message.from_user.id

        if action == "create_invoice":
            await message.answer("⏳ Генерирую адрес...")
            
            # ТУТ ДОЛЖЕН БЫТЬ ЗАПРОС К API XROCKET
            # Для теста даем фейковый адрес
            address = "TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE"
            
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(address)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            bio = BytesIO()
            img.save(bio, format="PNG")
            bio.seek(0)
            
            await message.answer_photo(photo=BufferedInputFile(bio.read(), filename="qr.png"), caption=f"✅ **Адрес для пополнения (USDT TRC-20):**\n\n`{address}`", parse_mode="Markdown")

        elif action == "add_balance" and uid in ADMIN_IDS:
            target_id = int(data.get("target_id"))
            amount = float(data.get("amount"))
            await get_user(target_id)
            await update_balance(target_id, amount, "Пополнение админом")
            await message.answer(f"✅ Выдано `{amount}` USDT пользователю `{target_id}`.", parse_mode="Markdown")
            try:
                await bot.send_message(target_id, f"🎁 Вам начислено {amount} USDT!")
            except: pass

        elif action == "toggle_ban" and uid in ADMIN_IDS:
            target_id = int(data.get("target_id"))
            user = await get_user(target_id)
            new_status = 0 if user["is_banned"] else 1
            async with aiosqlite.connect(DB_NAME) as db:
                await db.execute("UPDATE users SET is_banned = ? WHERE user_id = ?", (new_status, target_id))
                await db.commit()
            await message.answer(f"✅ Статус `{target_id}` изменен.")

        elif action == "broadcast" and uid in ADMIN_IDS:
            text = data.get("text")
            async with aiosqlite.connect(DB_NAME) as db:
                async with db.execute("SELECT user_id FROM users") as cursor:
                    all_users = await cursor.fetchall()
            sent = 0
            for u in all_users:
                try:
                    await bot.send_message(u[0], f"📢 {text}")
                    sent += 1
                except: pass
            await message.answer(f"✅ Рассылка отправлена `{sent}` пользователям.")

        elif action == "get_history":
            history = await get_history(uid)
            if not history:
                await message.answer("📜 История пуста.")
            else:
                text = "📜 **История:**\n\n"
                for h in history:
                    text += f"• {h[2]} | {h[0]}: `{h[1]}` USDT\n"
                await message.answer(text, parse_mode="Markdown")

        elif action == "ref_link":
            bot_info = await bot.get_me()
            ref_link = f"https://t.me/{bot_info.username}?start={uid}"
            await message.answer(f"👥 Твоя ссылка:\n`{ref_link}`", parse_mode="Markdown")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

# ==================== ВЕБ-СЕРВЕР ====================
async def handle(request):
    return web.Response(text="Bot is alive!")

async def main():
    await init_db()
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 8080)))
    await site.start()
    print("Bot started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
