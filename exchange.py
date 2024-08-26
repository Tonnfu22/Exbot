import requests
from config import CRYPTO_API_KEY

def get_exchange_rate(currency: str) -> float:
    url = f"https://api.crypto.com/v2/public/get-ticker?instrument_name={currency}_USD"
    response = requests.get(url, headers={"Authorization": f"Bearer {CRYPTO_API_KEY}"})
    data = response.json()
    return data['data']['price']