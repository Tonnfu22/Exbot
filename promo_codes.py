PROMO_CODES = {
    "DISCOUNT10": 0.9,  # 10% скидка
    "BONUS5": 1.05      # 5% бонус
}

def apply_promo_code(amount: float, code: str) -> float:
    discount = PROMO_CODES.get(code.upper(), 1)
    return amount * discount