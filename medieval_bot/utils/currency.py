def convert_to_copper(platinum=0, gold=0, silver=0, copper=0):
    """Конвертация всех валют в медные"""
    total = copper
    total += silver * 100
    total += gold * 10000
    total += platinum * 1000000
    return total

def convert_from_copper(copper_amount):
    """Конвертация медных в красивый формат"""
    platinum = copper_amount // 1000000
    remainder = copper_amount % 1000000
    
    gold = remainder // 10000
    remainder = remainder % 10000
    
    silver = remainder // 100
    copper = remainder % 100
    
    return {
        'platinum': platinum,
        'gold': gold,
        'silver': silver,
        'copper': copper
    }

def format_currency(copper_amount):
    """Форматирование для отображения"""
    currencies = convert_from_copper(copper_amount)
    result = []
    
    if currencies['platinum'] > 0:
        result.append(f"💎 {currencies['platinum']} плат.")
    if currencies['gold'] > 0:
        result.append(f"🟡 {currencies['gold']} зол.")
    if currencies['silver'] > 0:
        result.append(f"⚪ {currencies['silver']} сер.")
    if currencies['copper'] > 0 or not result:
        result.append(f"🟤 {currencies['copper']} мед.")
    
    return " ".join(result)

def get_currency_emoji(currency_type: str) -> str:
    """Получить эмодзи для типа валюты"""
    emojis = {
        'copper': '🟤',
        'silver': '⚪',
        'gold': '🟡',
        'platinum': '💎'
    }
    return emojis.get(currency_type, '🟤')
