import os
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from dotenv import load_dotenv
from config import CRYPTO_API_KEY

# Загружаем переменные из .env файла
load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")

if not API_TOKEN:
    raise ValueError("Необходимо установить BOT_TOKEN в файле .env")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Словарь для хранения информации о пользователях
users = {}

# Промокоды и скидки
promo_codes = {
    "DISCOUNT10": 0.1,
    "WELCOME15": 0.15
}
user_promos = {}

# Клавиатура для главного меню
main_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Обмен валют", callback_data="exchange")],
        [InlineKeyboardButton(text="Проверка баланса", callback_data="balance")],
        [InlineKeyboardButton(text="Промокод", callback_data="promo")]
    ]
)

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    users[user_id] = {"balance": 0, "promocode": None}
    await message.reply("Добро пожаловать в наш обменник!\nВыберите команду из меню ниже:", reply_markup=main_menu_kb)

@dp.callback_query(lambda c: c.data == "exchange")
async def process_exchange(callback_query: CallbackQuery):
    await callback_query.message.answer("Введите сумму и валюты для обмена, например: /exchange 1 BTC USDT")

@dp.callback_query(lambda c: c.data == "balance")
async def process_balance(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    balance = users.get(user_id, {}).get("balance", 0)
    await callback_query.message.answer(f"Ваш текущий баланс: {balance} USDT.")

@dp.callback_query(lambda c: c.data == "promo")
async def process_promo(callback_query: CallbackQuery):
    await callback_query.message.answer("Введите ваш промокод, например: /promo DISCOUNT10")

@dp.message(Command("promo"))
async def promo_handler(message: types.Message):
    user_id = message.from_user.id
    args = message.text.split()
    
    if len(args) < 2:
        await message.reply("Пожалуйста, укажите промокод.")
        return
    
    code = args[1].upper()
    discount = promo_codes.get(code)
    
    if discount:
        user_promos[user_id] = discount
        await message.reply(f"Промокод применён! Ваша скидка: {discount * 100}%.")
    else:
        await message.reply("Промокод недействителен.")

@dp.message(Command("exchange"))
async def exchange_handler(message: types.Message):
    user_id = message.from_user.id
    args = message.text.split()

    if len(args) < 4:
        await message.reply("Пожалуйста, укажите сумму и валюты для обмена (например, /exchange 1 BTC USDT).")
        return

    amount = float(args[1])
    from_currency = args[2].upper()
    to_currency = args[3].upper()

    if users[user_id]["balance"] < amount:
        await message.reply("Недостаточно средств на балансе.")
        return

    # Получение курса обмена через API
    from_rate = get_exchange_rate(from_currency)
    to_rate = get_exchange_rate(to_currency)
    result = amount * (from_rate / to_rate)

    discount = user_promos.get(user_id, 0)
    final_result = result * (1 - discount)

    users[user_id]["balance"] -= amount
    await message.reply(f"Курс обмена: 1 {from_currency} = {from_rate} USDT\n"
                        f"Вы получите: {final_result:.2f} {to_currency} (С учетом скидки {discount * 100}%)")

def get_exchange_rate(currency: str) -> float:
    url = f"https://api.crypto.com/v2/public/get-ticker?instrument_name={currency}_USDT"
    response = requests.get(url, headers={"Authorization": f"Bearer {CRYPTO_API_KEY}"})
    data = response.json()
    return float(data['data']['last'])

async def main():
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())
