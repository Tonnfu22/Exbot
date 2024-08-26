from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN
from exchange import get_exchange_rate
from promo_codes import apply_promo_code

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Создание главного меню
def main_menu():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("💱 Обмен", callback_data="exchange"))
    keyboard.add(InlineKeyboardButton("💰 Баланс", callback_data="balance"))
    keyboard.add(InlineKeyboardButton("🎁 Промокод", callback_data="promo_code"))
    keyboard.add(InlineKeyboardButton("ℹ️ Информация", callback_data="info"))
    return keyboard

# Обработчик команды /start
@dp.message(Command("start"))
async def start(message: Message):
    await message.reply("Добро пожаловать в Crypto Exchange Bot!", reply_markup=main_menu())

# Обработчик нажатия на кнопки
@dp.callback_query_handler(lambda callback_query: True)
async def handle_callback_query(callback_query: types.CallbackQuery):
    data = callback_query.data

    if data == "exchange":
        await callback_query.message.answer("Введите сумму и валюту для обмена (например, 100 BTC):")
    elif data == "balance":
        await callback_query.message.answer("Ваш текущий баланс: 0.00 USD")  # Здесь нужно подключить реальную логику получения баланса
    elif data == "promo_code":
        await callback_query.message.answer("Введите промокод:")
    elif data == "info":
        await callback_query.message.answer("Этот бот позволяет обменивать криптовалюты, проверять баланс и использовать промокоды.")

# Обработчик текстовых сообщений (обмен и промокоды)
@dp.message_handler()
async def handle_text(message: Message):
    text = message.text.strip().split()
    
    if len(text) == 2:
        # Обмен валют
        try:
            amount = float(text[0])
            currency = text[1].upper()
            rate = get_exchange_rate(currency)
            result = amount * rate
            await message.reply(f"{amount} {currency} = {result:.2f} USD")
        except Exception as e:
            await message.reply("Ошибка: Неправильный формат или неизвестная валюта.")
    elif len(text) == 1:
        # Применение промокода
        promo_code = text[0].upper()
        discount = apply_promo_code(100, promo_code)  # Используем 100 как тестовую сумму
        if discount < 100:
            await message.reply(f"Промокод применен! Ваша скидка: {100 - discount:.2f} USD")
        else:
            await message.reply("Неверный промокод.")
    else:
        await message.reply("Пожалуйста, введите корректные данные.")

async def main():
    dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
