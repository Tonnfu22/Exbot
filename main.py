from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
import os
import asyncio

# Загружаем переменные из .env файла
load_dotenv()

# Получаем токен бота из переменных окружения
API_TOKEN = os.getenv("BOT_TOKEN")

# Проверяем, что токен был загружен
if not API_TOKEN:
    raise ValueError("Необходимо установить BOT_TOKEN в файле .env")

# Создаем экземпляр бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Словарь для хранения информации о пользователях
users = {}

# Промокоды и скидки
promo_codes = {
    "DISCOUNT10": 0.1,  # 10% скидка
    "WELCOME15": 0.15   # 15% скидка
}
user_promos = {}

# Клавиатура для главного меню
main_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Обмен валют", callback_data="exchange")],
        [InlineKeyboardButton(text="Пополнение баланса", callback_data="deposit")],
        [InlineKeyboardButton(text="Вывод средств", callback_data="withdraw")],
        [InlineKeyboardButton(text="Проверить баланс", callback_data="balance")]
    ]
)

# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: Message):
    user_id = message.from_user.id
    users[user_id] = {
        "balance": 0,    # Начальный баланс
        "promocode": None  # Промокод пользователя
    }
    await message.reply("Добро пожаловать в наш крипто-обменник!\n"
                        "Выберите команду из меню ниже:", reply_markup=main_menu_kb)

# Обработчик кнопок главного меню
@dp.callback_query_handler(lambda c: c.data in ['exchange', 'deposit', 'withdraw', 'balance'])
async def process_menu_buttons(callback_query: types.CallbackQuery):
    action = callback_query.data
    user_id = callback_query.from_user.id

    if action == 'exchange':
        await callback_query.message.answer("Введите сумму и валюты для обмена, например: /exchange 1 BTC ETH")
    elif action == 'deposit':
        await callback_query.message.answer("Введите сумму для пополнения, например: /deposit 1000")
    elif action == 'withdraw':
        await callback_query.message.answer("Введите сумму и адрес для вывода, например: /withdraw 1000 1A1zP1...n4MT5")
    elif action == 'balance':
        balance = users.get(user_id, {}).get("balance", 0)
        await callback_query.message.answer(f"Ваш текущий баланс: {balance} единиц.")

# Обработчик команды /promo
@dp.message(Command("promo"))
async def promo_handler(message: Message):
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

# Обработчик команды /exchange
@dp.message(Command("exchange"))
async def exchange_handler(message: Message):
    user_id = message.from_user.id
    args = message.text.split()

    if len(args) < 4:
        await message.reply("Пожалуйста, укажите сумму и валюты для обмена (например, /exchange 1 BTC ETH).")
        return

    amount = float(args[1])
    from_currency = args[2].upper()
    to_currency = args[3].upper()

    if users[user_id]["balance"] < amount:
        await message.reply("Недостаточно средств на балансе.")
        return

    # Логика получения курса обмена
    example_rate = 30000  # Например, курс 1 BTC = 30000 USDT
    result = amount * example_rate

    discount = user_promos.get(user_id, 0)
    final_result = result * (1 - discount)

    users[user_id]["balance"] -= amount
    await message.reply(f"Курс обмена: {example_rate}\n"
                        f"Вы получите: {final_result} {to_currency} (С учетом скидки {discount * 100}%)")

# Обработчик команды /deposit
@dp.message(Command("deposit"))
async def deposit_handler(message: Message):
    user_id = message.from_user.id
    args = message.text.split()

    if len(args) < 2:
        await message.reply("Пожалуйста, укажите сумму для пополнения (например, /deposit 1000).")
        return

    amount = float(args[1])
    users[user_id]["balance"] += amount

    await message.reply(f"Ваш баланс пополнен на {amount} единиц. Текущий баланс: {users[user_id]['balance']} единиц.")

# Обработчик команды /withdraw
@dp.message(Command("withdraw"))
async def withdraw_handler(message: Message):
    user_id = message.from_user.id
    args = message.text.split()

    if len(args) < 3:
        await message.reply("Пожалуйста, укажите сумму и адрес для вывода (например, /withdraw 1000 1A1zP1...n4MT5).")
        return

    amount = float(args[1])
    address = args[2]

    if users[user_id]["balance"] < amount:
        await message.reply("Недостаточно средств на балансе.")
        return

    users[user_id]["balance"] -= amount
    await message.reply(f"Средства в размере {amount} единиц отправлены на адрес {address}. Текущий баланс: {users[user_id]['balance']} единиц.")

# Обработчик команды /help
@dp.message(Command("help"))
async def help_handler(message: Message):
    await message.reply("Команды:\n"
                        "/start - Начало работы\n"
                        "/exchange - Обмен валют\n"
                        "/promo - Применить промокод\n"
                        "/deposit - Пополнить баланс\n"
                        "/withdraw - Вывести средства\n"
                        "/balance - Проверить баланс\n"
                        "/help - Помощь")

async def main():
    # Запуск бота
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
