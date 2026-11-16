import asyncio
import os
import aiohttp
import aiosqlite
import json
from datetime import datetime
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.environ.get("BOT_TOKEN", "ТВОЙ_ТОКЕН")
ADMIN_IDS = [8636027393]
WEBAPP_URL = "https://cryptoapp32155.vercel.app"
XROCKET_PAY_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHAiOiIweDAiLCJ1c2VySWQiOiIxNDE0NjAyNyIsImp0aSI6InVzZXI6MTQxNDYwMjc6ZjQ5NDk2ZWItMmQ3NS00NmIyLWI1OTUtZGM3YTA2ODdjZmQ2IiwidHlwZSI6ImV4Y2hhbmdlIiwicGxhdGZvcm0iOiJleGNoYW5nZV9hcGkiLCJpYXQiOjE3OTQ0Mjk3MzR9.gF1vaCUb3Q48UtS2z2RvOwDtZOYelLGtpQzMw_2bmTI" 

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
DB_NAME = "database.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance REAL DEFAULT 0.0, is_banned INTEGER DEFAULT 0)")
        await db.execute("CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, type TEXT, amount REAL, date TEXT)")
        await db.execute("CREATE TABLE IF NOT EXISTS checks (code TEXT PRIMARY KEY, amount REAL, is_used INTEGER DEFAULT 0, used_by INTEGER DEFAULT NULL)")
        await db.commit()

# ==================== API ДЛЯ MINI APP ====================
async def api_get_prices(request):
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,binancecoin,ripple,dogecoin,cardano,the-open-network,tron,polkadot&vs_currencies=usd&include_24hr_change=true"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                return web.json_response(data)
    except Exception as e:
        return web.json_response({"error": str(e)})

async def api_create_invoice(request):
    try:
        data = await request.json()
        uid = data.get("user_id")
        url = "https://pay.api.xrocket.exchange/api/v1/invoices"
        headers = {"Authorization": f"Bearer {XROCKET_PAY_KEY}", "Content-Type": "application/json"}
        payload = {"currency": "USDT", "amount": 10.0, "description": "Deposit", "payload": str(uid), "expiredIn": 86400}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                if resp.status == 200:
                    inv_data = await resp.json()
                    inv_id = inv_data.get("data", {}).get("id") or inv_data.get("id")
                    addr_url = "https://pay.api.xrocket.exchange/api/v1/invoices/payments/address"
                    addr_payload = {"invoiceId": inv_id, "payNetwork": "TRC20"}
                    async with session.post(addr_url, json=addr_payload, headers=headers) as resp:
                        addr_data = await resp.json()
                        address = addr_data.get("address") or addr_data.get("data", {}).get("address")
                        if address: return web.json_response({"address": address})
        return web.json_response({"error": "Ошибка xRocket"}, status=400)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def api_get_ref(request):
    bot_info = await bot.get_me()
    return web.json_response({"bot_username": bot_info.username})

async def api_get_history(request):
    uid = request.query.get('user_id')
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT type, amount, date FROM history WHERE user_id = ? ORDER BY id DESC LIMIT 20", (uid,)) as cursor:
            rows = await cursor.fetchall()
            history = [{"type": r[0], "amount": r[1], "date": r[2]} for r in rows]
            return web.json_response({"history": history})

async def api_activate_check(request):
    try:
        data = await request.json()
        code = data.get("code")
        uid = data.get("user_id")
        async with aiosqlite.connect(DB_NAME) as db:
            async with db.execute("SELECT amount, is_used FROM checks WHERE code = ?", (code,)) as cursor:
                check = await cursor.fetchone()
                if not check: return web.json_response({"error": "Чек не найден"})
                if check[1] == 1: return web.json_response({"error": "Этот чек уже активирован"})
                amount = check[0]
                await db.execute("UPDATE checks SET is_used = 1, used_by = ? WHERE code = ?", (uid, code))
                await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, uid))
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                await db.execute("INSERT INTO history (user_id, type, amount, date) VALUES (?, 'Чек', ?, ?)", (uid, amount, now))
                await db.commit()
                return web.json_response({"success": True, "amount": amount})
    except Exception as e:
        return web.json_response({"error": str(e)})

async def api_admin_create_check(request):
    data = await request.json()
    if data.get("admin_code") != "19091977": return web.json_response({"error": "Нет доступа"})
    code = data.get("check_name")
    amount = float(data.get("amount"))
    async with aiosqlite.connect(DB_NAME) as db:
        try:
            await db.execute("INSERT INTO checks (code, amount) VALUES (?, ?)", (code, amount))
            await db.commit()
            return web.json_response({"success": True})
        except:
            return web.json_response({"error": "Такой код уже есть"})

async def api_admin_action(request):
    data = await request.json()
    if data.get("admin_code") != "19091977": return web.json_response({"error": "Нет доступа"})
    action = data.get("action")
    target_id = data.get("target_id")
    amount = data.get("amount")
    text = data.get("text")
    
    async with aiosqlite.connect(DB_NAME) as db:
        if action == "add_balance":
            await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (float(amount), int(target_id)))
            await db.execute("INSERT INTO history (user_id, type, amount, date) VALUES (?, 'Пополнение', ?, datetime('now'))", (int(target_id), float(amount)))
            await db.commit()
            try: await bot.send_message(int(target_id), f"🎁 Вам начислено {amount} USDT!")
            except: pass
            return web.json_response({"success": True})
        elif action == "sub_balance":
            await db.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (float(amount), int(target_id)))
            await db.commit()
            return web.json_response({"success": True})
        elif action == "ban":
            await db.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (int(target_id),))
            await db.commit()
            return web.json_response({"success": True})
        elif action == "unban":
            await db.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (int(target_id),))
            await db.commit()
            return web.json_response({"success": True})
        elif action == "broadcast":
            async with db.execute("SELECT user_id FROM users") as cursor:
                users = await cursor.fetchall()
            sent = 0
            for u in users:
                try: 
                    await bot.send_message(u[0], f"📢 {text}")
                    sent += 1
                except: pass
            return web.json_response({"success": True, "sent": sent})
    return web.json_response({"error": "Неизвестное действие"})

# ==================== ВЕБ-СЕРВЕР ====================
async def handle(request): return web.Response(text="Bot is alive!")

async def main():
    await init_db()
    app = web.Application()
    app.router.add_get("/", handle)
    app.router.add_get("/api/prices", api_get_prices)
    app.router.add_post("/api/create_invoice", api_create_invoice)
    app.router.add_get("/api/ref", api_get_ref)
    app.router.add_get("/api/history", api_get_history)
    app.router.add_post("/api/activate_check", api_activate_check)
    app.router.add_post("/api/admin/create_check", api_admin_create_check)
    app.router.add_post("/api/admin/action", api_admin_action)
    
    async def cors_middleware(app, handler):
        async def middleware_handler(request):
            if request.method == "OPTIONS": response = web.Response()
            else: response = await handler(request)
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            return response
        return middleware_handler

    app.middlewares.append(cors_middleware)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 8080)))
    await site.start()
    
    print("Бот запущен!")
    await dp.start_polling(bot)

@dp.message(Command("start"))
async def start(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🚀 Открыть", web_app=WebAppInfo(url=WEBAPP_URL))]])
    await message.answer("Добро пожаловать!", reply_markup=kb)

if __name__ == "__main__":
    asyncio.run(main())
