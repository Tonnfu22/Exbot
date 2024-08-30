from aiogram import Bot, Dispatcher, types
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

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    users[user_id] = {
        "balance": 0,    # Начальный баланс
        "promocode": None  # Промокод пользователя
    }
    await message.reply("Добро пожаловать в наш крипто-обменник!\n"
                        "Для обмена валют используйте команду /exchange.\n"
                        "Для использования промокода введите команду /promo [код].\n"
                        "Для пополнения счета используйте команду /deposit.\n"
                        "Для вывода средств используйте команду /withdraw.")

# Обработчик команды /promo
@dp.message_handler(commands=['promo'])
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

# Обработчик команды /exchange
@dp.message_handler(commands=['exchange'])
async def exchange_handler(message: types.Message):
    user_id = message.from_user.id
    args = message.text.split()

    if len(args) < 4:
        await message.reply("Пожалуйста, укажите сумму и валюты для обмена (например, /exchange 1 BTC ETH).")
        return

    amount = float(args[1])
    from_currency = args[2].upper()
    to_currency = args[3].upper()

    # Проверка баланса (пример placeholder)
    if users[user_id]["balance"] < amount:
        await message.reply("Недостаточно средств на балансе.")
        return

    # Здесь может быть логика получения курса обмена, например, через API биржи
    example_rate = 30000  # Например, курс 1 BTC = 30000 USDT
    result = amount * example_rate

    # Применение скидки, если промокод активен
    discount = user_promos.get(user_id, 0)
    final_result = result * (1 - discount)

    # Обновляем баланс (пример placeholder)
    users[user_id]["balance"] -= amount
    await message.reply(f"Курс обмена: {example_rate}\n"
                        f"Вы получите: {final_result} {to_currency} (С учетом скидки {discount * 100}%)")

# Обработчик команды /deposit
@dp.message_handler(commands=['deposit'])
async def deposit_handler(message: types.Message):
    user_id = message.from_user.id
    args = message.text.split()

    if len(args) < 2:
        await message.reply("Пожалуйста, укажите сумму для пополнения (например, /deposit 1000).")
        return

    amount = float(args[1])
    users[user_id]["balance"] += amount  # Обновляем баланс пользователя

    await message.reply(f"Ваш баланс пополнен на {amount} единиц. Текущий баланс: {users[user_id]['balance']} единиц.")

# Обработчик команды /withdraw
@dp.message_handler(commands=['withdraw'])
async def withdraw_handler(message: types.Message):
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

    # Обновляем баланс пользователя
    users[user_id]["balance"] -= amount
    await message.reply(f"Средства в размере {amount} единиц отправлены на адрес {address}. Текущий баланс: {users[user_id]['balance']} единиц.")

# Обработчик команды /balance
@dp.message_handler(commands=['balance'])
async def balance_handler(message: types.Message):
    user_id = message.from_user.id
    balance = users[user_id]["balance"]
    await message.reply(f"Ваш текущий баланс: {balance} единиц.")

# Обработчик команды /help
@dp.message_handler(commands=['help'])
async def help_handler(message: types.Message):
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
    await bot.delete_webhook()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
