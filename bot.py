
import asyncio
from datetime import datetime, timedelta
from aiohttp import web

from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --------------------------------------------
#                НАСТРОЙКИ
# --------------------------------------------

API_TOKEN = "8505621265:AAHho15Z7ExE8ZSbvZuORSt8sNMejdMGnBI" 
GROUP_CHAT_ID = -5074126218   # группа CRM

# --------------------------------------------
#                БОТ + РОУТЕР
# --------------------------------------------

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Хранилище таймеров поиска и напоминаний по заказу
active_search_timers = {}
active_order_timers = {}

# --------------------------------------------
#     Красивые кнопки под заявкой (CRM UI)
# --------------------------------------------

def crm_buttons(application_id: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="🎀 Начат поиск", callback_data=f"search:{application_id}")
    kb.button(text="👶 Кидсистер найден", callback_data=f"found:{application_id}")
    kb.button(text="💳 Заказ оплачен", callback_data=f"paid:{application_id}")
    kb.adjust(1)
    return kb.as_markup()

# --------------------------------------------
#       Красивое оформление заявки Tilda
# --------------------------------------------

def format_application(data: dict):
    text = "🍼 *Новая заявка Kidsister*\n\n"
    for k, v in data.items():
        text += f"• *{k}:* {v}\n"
    return text

# --------------------------------------------
#     Логика таймера «Начат поиск»
# --------------------------------------------

async def start_search_timer(application_id: str):
    while application_id in active_search_timers:
        await asyncio.sleep(2 * 60 * 60)  # 2 часа
        if application_id in active_search_timers:
            await bot.send_message(
                GROUP_CHAT_ID,
                f"🔔 Напоминание по заявке *{application_id}*:\n"
                f"Пожалуйста, обновите информацию по клиенту 💕",
                parse_mode="Markdown"
            )

# --------------------------------------------
#     Логика таймера после оплаты
# --------------------------------------------

async def start_post_order_timer(application_id: str, date_time: datetime):
    now = datetime.now()
    delay = (date_time + timedelta(minutes=30)) - now

    delay_seconds = max(delay.total_seconds(), 0)
    await asyncio.sleep(delay_seconds)

    if application_id in active_order_timers:
        await bot.send_message(
            GROUP_CHAT_ID,
            f"✨ Напоминание по заказу *{application_id}*!\n\n"
            f"Проверь, всё ли прошло хорошо 💕\n"
            f"Попроси отзыв и предложи развивающие занятия 🌸",
            parse_mode="Markdown"
        )

# --------------------------------------------
#     Обработка Tilda Webhook (/webhook)
# --------------------------------------------

async def handle_webhook(request):
    data = await request.json()

    application_id = str(datetime.now().timestamp()).replace(".", "")

    formatted = format_application(data)

    await bot.send_message(
        GROUP_CHAT_ID,
        formatted,
        parse_mode="Markdown",
        reply_markup=crm_buttons(application_id)
    )

    return web.Response(text="OK")

# --------------------------------------------
#        ХЕНДЛЕРЫ ДЛЯ CRM-КНОПОК
# --------------------------------------------

@router.callback_query()
async def callbacks(call: types.CallbackQuery):
    action, application_id = call.data.split(":")

    # ------------------ 🎀 Начат поиск ------------------
    if action == "search":
        active_search_timers[application_id] = True

        await bot.send_message(
            GROUP_CHAT_ID,
            f"🎀 Поиск няни начат по заявке *{application_id}*!",
            parse_mode="Markdown"
        )

        asyncio.create_task(start_search_timer(application_id))

    # ------------------ 👶 Кидсистер найден ------------------
    elif action == "found":
        active_search_timers.pop(application_id, None)

        await bot.send_message(
            GROUP_CHAT_ID,
            f"👶 Исполнитель найден по заявке *{application_id}*!",
            parse_mode="Markdown"
        )

    # ------------------ 💳 Заказ оплачен ------------------
    elif action == "paid":
        active_search_timers.pop(application_id, None)

        await bot.send_message(
            GROUP_CHAT_ID,
            f"💳 Заказ оплачен по заявке *{application_id}*!\n\n"
            f"Введите дату и время услуги в формате:\n"
            f"`24.02.2025 14:30`",
            parse_mode="Markdown"
        )

        active_order_timers[call.from_user.id] = application_id

    await call.answer()

# --------------------------------------------
#    Обработка ввода даты и времени после оплаты
# --------------------------------------------

@router.message()
async def process_datetime(message: types.Message):
    if message.from_user.id not in active_order_timers:
        return

    application_id = active_order_timers.pop(message.from_user.id)

    try:
        dt = datetime.strptime(message.text, "%d.%m.%Y %H:%M")

        asyncio.create_task(start_post_order_timer(application_id, dt))

        await message.answer(
            f"🕒 Время услуги сохранено!\n"
            f"Через 30 минут после неё я пришлю напоминание 💕"
        )
    except ValueError:
        await message.answer("❌ Неверный формат. Пример: 24.02.2025 14:30")

# --------------------------------------------
#                ЗАПУСК СЕРВЕРА
# --------------------------------------------

async def main():
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

    print("🌸 Webhook сервер запущен!")

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
from datetime import datetime, timedelta
from aiohttp import web

from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --------------------------------------------
#                НАСТРОЙКИ
# --------------------------------------------

API_TOKEN = "8505621265:AAHho15Z7ExE8ZSbvZuORSt8sNMejdMGnBI" 
GROUP_CHAT_ID = -5074126218   # группа CRM

# --------------------------------------------
#                БОТ + РОУТЕР
# --------------------------------------------

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Хранилище таймеров поиска и напоминаний по заказу
active_search_timers = {}
active_order_timers = {}

# --------------------------------------------
#     Красивые кнопки под заявкой (CRM UI)
# --------------------------------------------

def crm_buttons(application_id: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="🎀 Начат поиск", callback_data=f"search:{application_id}")
    kb.button(text="👶 Кидсистер найден", callback_data=f"found:{application_id}")
    kb.button(text="💳 Заказ оплачен", callback_data=f"paid:{application_id}")
    kb.adjust(1)
    return kb.as_markup()

# --------------------------------------------
#       Красивое оформление заявки Tilda
# --------------------------------------------

def format_application(data: dict):
    text = "🍼 *Новая заявка Kidsister*\n\n"
    for k, v in data.items():
        text += f"• *{k}:* {v}\n"
    return text

# --------------------------------------------
#     Логика таймера «Начат поиск»
# --------------------------------------------

async def start_search_timer(application_id: str):
    while application_id in active_search_timers:
        await asyncio.sleep(2 * 60 * 60)  # 2 часа
        if application_id in active_search_timers:
            await bot.send_message(
                GROUP_CHAT_ID,
                f"🔔 Напоминание по заявке *{application_id}*:\n"
                f"Пожалуйста, обновите информацию по клиенту 💕",
                parse_mode="Markdown"
            )

# --------------------------------------------
#     Логика таймера после оплаты
# --------------------------------------------

async def start_post_order_timer(application_id: str, date_time: datetime):
    now = datetime.now()
    delay = (date_time + timedelta(minutes=30)) - now

    delay_seconds = max(delay.total_seconds(), 0)
    await asyncio.sleep(delay_seconds)

    if application_id in active_order_timers:
        await bot.send_message(
            GROUP_CHAT_ID,
            f"✨ Напоминание по заказу *{application_id}*!\n\n"
            f"Проверь, всё ли прошло хорошо 💕\n"
            f"Попроси отзыв и предложи развивающие занятия 🌸",
            parse_mode="Markdown"
        )

# --------------------------------------------
#     Обработка Tilda Webhook (/webhook)
# --------------------------------------------

async def handle_webhook(request):
    data = await request.json()

    application_id = str(datetime.now().timestamp()).replace(".", "")

    formatted = format_application(data)

    await bot.send_message(
        GROUP_CHAT_ID,
        formatted,
        parse_mode="Markdown",
        reply_markup=crm_buttons(application_id)
    )

    return web.Response(text="OK")

# --------------------------------------------
#        ХЕНДЛЕРЫ ДЛЯ CRM-КНОПОК
# --------------------------------------------

@router.callback_query()
async def callbacks(call: types.CallbackQuery):
    action, application_id = call.data.split(":")

    # ------------------ 🎀 Начат поиск ------------------
    if action == "search":
        active_search_timers[application_id] = True

        await bot.send_message(
            GROUP_CHAT_ID,
            f"🎀 Поиск няни начат по заявке *{application_id}*!",
            parse_mode="Markdown"
        )

        asyncio.create_task(start_search_timer(application_id))

    # ------------------ 👶 Кидсистер найден ------------------
    elif action == "found":
        active_search_timers.pop(application_id, None)

        await bot.send_message(
            GROUP_CHAT_ID,
            f"👶 Исполнитель найден по заявке *{application_id}*!",
            parse_mode="Markdown"
        )

    # ------------------ 💳 Заказ оплачен ------------------
    elif action == "paid":
        active_search_timers.pop(application_id, None)

        await bot.send_message(
            GROUP_CHAT_ID,
            f"💳 Заказ оплачен по заявке *{application_id}*!\n\n"
            f"Введите дату и время услуги в формате:\n"
            f"`24.02.2025 14:30`",
            parse_mode="Markdown"
        )

        active_order_timers[call.from_user.id] = application_id

    await call.answer()

# --------------------------------------------
#    Обработка ввода даты и времени после оплаты
# --------------------------------------------

@router.message()
async def process_datetime(message: types.Message):
    if message.from_user.id not in active_order_timers:
        return

    application_id = active_order_timers.pop(message.from_user.id)

    try:
        dt = datetime.strptime(message.text, "%d.%m.%Y %H:%M")

        asyncio.create_task(start_post_order_timer(application_id, dt))

        await message.answer(
            f"🕒 Время услуги сохранено!\n"
            f"Через 30 минут после неё я пришлю напоминание 💕"
        )
    except ValueError:
        await message.answer("❌ Неверный формат. Пример: 24.02.2025 14:30")

# --------------------------------------------
#                ЗАПУСК СЕРВЕРА
# --------------------------------------------

async def main():
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

    print("🌸 Webhook сервер запущен!")

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())

