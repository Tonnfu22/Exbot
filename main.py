from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from config import BOT_TOKEN
from exchange import get_exchange_rate
from promo_codes import apply_promo_code

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Welcome to the Crypto Exchange Bot!")

@dp.message_handler(commands=['exchange'])
async def exchange(message: types.Message):
    # Пример обмена с использованием промокода
    args = message.get_args().split()
    if len(args) < 2:
        await message.reply("Please provide amount and currency.")
        return
    
    amount = float(args[0])
    currency = args[1]
    promo_code = args[2] if len(args) > 2 else None
    
    rate = get_exchange_rate(currency)
    result = amount * rate
    
    if promo_code:
        result = apply_promo_code(result, promo_code)
    
    await message.reply(f"{amount} {currency} = {result:.2f} USD")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)