from pyrogram import Client, filters
import ccxt

# Настройки API и токен бота
app = Client("crypto_exchange_bot", api_id="ВАШ_API_ID", api_hash="ВАШ_API_HASH", bot_token="ВАШ_БОТ_ТОКЕН")

# Инициализация системы промокодов
promo_codes = {
    "DISCOUNT10": 0.1,  # 10% скидка
    "WELCOME15": 0.15   # 15% скидка
}

# Подключение к бирже (Binance в данном случае)
exchange = ccxt.binance()

# Хранение активных промокодов для пользователей
user_promos = {}

# Приветственное сообщение
@app.on_message(filters.command("start"))
def start(client, message):
    message.reply("Добро пожаловать в наш крипто-обменник! Используйте команду /exchange для обмена валют.\n"
                  "Для использования промокода, введите команду /promo [код].")

# Обработка команды промокода
@app.on_message(filters.command("promo"))
def promo(client, message):
    user_id = message.from_user.id
    code = message.text.split()[1].upper()  # Получаем промокод от пользователя
    discount = promo_codes.get(code)

    if discount:
        user_promos[user_id] = discount
        message.reply(f"Промокод применён! Ваша скидка: {discount * 100}%.")
    else:
        message.reply("Промокод недействителен.")

# Команда для обмена валют
@app.on_message(filters.command("exchange"))
def exchange_command(client, message):
    user_id = message.from_user.id
    args = message.text.split()

    if len(args) < 4:
        message.reply("Пожалуйста, укажите сумму и валюты (например, /exchange 1 BTC ETH).")
        return

    amount = float(args[1])
    from_currency = args[2].upper()
    to_currency = args[3].upper()

    # Получаем курс обмена
    ticker = exchange.fetch_ticker(f"{from_currency}/{to_currency}")
    rate = ticker['last']

    result = amount * rate

    # Применение скидки, если промокод активен
    discount = user_promos.get(user_id, 0)
    final_result = result * (1 - discount)

    message.reply(f"Курс: {rate}\nВы получите: {final_result} {to_currency} (С учетом скидки {discount * 100}%)")

# Обработка ввода/вывода средств (пример placeholder)
@app.on_message(filters.command("deposit"))
def deposit(client, message):
    message.reply("Пожалуйста, отправьте криптовалюту на указанный адрес.")

@app.on_message(filters.command("withdraw"))
def withdraw(client, message):
    message.reply("Введите сумму и адрес, на который хотите вывести средства.")

# Запуск бота
app.run()
