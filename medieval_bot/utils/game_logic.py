import random
from typing import Dict, Tuple, List

def calculate_luck_bonus(luck: int) -> float:
    """Расчёт бонуса от удачи (1-10% в зависимости от характеристики)"""
    return 1 + (luck / 1000)

def axe_throwing_game(luck: int) -> Tuple[str, float]:
    """
    Игра: Метание топоров
    Возвращает: (зона попадания, множитель)
    """
    base_chance = random.randint(1, 100)
    luck_bonus = calculate_luck_bonus(luck)
    final_chance = base_chance * luck_bonus
    
    if final_chance >= 95:
        return "🎯 Яблочко", 5.0
    elif final_chance >= 75:
        return "🟡 Внутренний круг", 3.0
    elif final_chance >= 50:
        return "🟠 Средний круг", 2.0
    elif final_chance >= 30:
        return "🔴 Внешний круг", 1.5
    else:
        return "⚫ Промах", 0.0

def dice_game() -> Tuple[List[int], str, float]:
    """
    Игра: Кости Судьбы
    Возвращает: (результаты кубиков, описание, множитель)
    """
    dice = [random.randint(1, 6) for _ in range(3)]
    dice_sum = sum(dice)
    
    if len(set(dice)) == 1:
        return dice, "🎲🎲🎲 ТРИ ОДИНАКОВЫХ", 10.0
    elif len(set(dice)) == 2:
        return dice, "🎲🎲 ДВА ОДИНАКОВЫХ", 3.0
    elif sorted(dice) in [[1, 2, 3], [4, 5, 6]]:
        return dice, "📊 СТРИТ", 5.0
    elif dice_sum >= 15:
        return dice, "🔥 ВЫСОКАЯ СУММА", 2.0
    else:
        return dice, "❌ НЕТ КОМБИНАЦИИ", 0.0

def generate_poker_hand() -> List[Dict[str, str]]:
    """Генерация покерной руки из 5 карт"""
    suits = ['🗡️', '⚔️', '🛡️', '🏹']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Валет', 'Дама', 'Король', 'Туз']
    
    deck = [{'suit': suit, 'rank': rank, 'value': idx + 2} 
            for idx, rank in enumerate(ranks) for suit in suits]
    
    return random.sample(deck, 5)

def evaluate_poker_hand(hand: List[Dict[str, str]]) -> Tuple[str, float, int]:
    """
    Оценка покерной руки
    Возвращает: (название комбинации, множитель, сила руки для сравнения)
    """
    ranks = [card['value'] for card in hand]
    suits = [card['suit'] for card in hand]
    rank_counts = {}
    for rank in ranks:
        rank_counts[rank] = rank_counts.get(rank, 0) + 1
    
    counts = sorted(rank_counts.values(), reverse=True)
    is_flush = len(set(suits)) == 1
    sorted_ranks = sorted(ranks)
    is_straight = (sorted_ranks[-1] - sorted_ranks[0] == 4 and len(set(ranks)) == 5)
    
    if is_straight and is_flush:
        if sorted_ranks == [10, 11, 12, 13, 14]:
            return "🏆 РОЯЛ-ФЛЕШ", 100.0, 10
        return "⚡ СТРИТ-ФЛЕШ", 50.0, 9
    
    if counts == [4, 1]:
        return "🎰 КАРЕ", 25.0, 8
    
    if counts == [3, 2]:
        return "🏠 ФУЛЛ-ХАУС", 15.0, 7
    
    if is_flush:
        return "💎 ФЛЕШ", 10.0, 6
    
    if is_straight:
        return "📊 СТРИТ", 7.0, 5
    
    if counts == [3, 1, 1]:
        return "🎲 ТРОЙКА", 5.0, 4
    
    if counts == [2, 2, 1]:
        return "👥 ДВЕ ПАРЫ", 3.0, 3
    
    if counts == [2, 1, 1, 1]:
        return "✌️ ПАРА", 2.0, 2
    
    return "🃏 СТАРШАЯ КАРТА", 1.0, 1

def target_shooting_game(agility: int) -> Tuple[int, float]:
    """
    Игра: Стрельба по мишеням (3 попытки)
    Возвращает: (количество попаданий, множитель)
    """
    hit_chance = min(70 + (agility / 10), 90)
    hits = sum(1 for _ in range(3) if random.random() * 100 < hit_chance)
    
    multipliers = {3: 5.0, 2: 2.0, 1: 1.0, 0: 0.0}
    return hits, multipliers[hits]

def roulette_spin() -> Tuple[int, str]:
    """
    Игра: Гладиаторская рулетка
    Возвращает: (номер, цвет)
    """
    number = random.randint(0, 36)
    if number == 0:
        color = 'black'
    elif number % 2 == 0:
        color = 'red'
    else:
        color = 'blue'
    
    return number, color

def check_roulette_bet(bet_type: str, bet_value: any, result_number: int, result_color: str) -> Tuple[bool, float]:
    """
    Проверка ставки в рулетке
    Возвращает: (выигрыш?, множитель)
    """
    if bet_type == 'number':
        if bet_value == result_number:
            return True, 35.0
    elif bet_type == 'color':
        if bet_value == result_color:
            return True, 2.0
    elif bet_type == 'zero':
        if result_number == 0:
            return True, 10.0
    elif bet_type == 'even':
        if result_number > 0 and result_number % 2 == 0:
            return True, 2.0
    elif bet_type == 'odd':
        if result_number > 0 and result_number % 2 == 1:
            return True, 2.0
    
    return False, 0.0

def rune_divination() -> Tuple[List[str], str, float]:
    """
    Игра: Гадание на рунах
    Возвращает: (3 выбранные руны, описание, множитель)
    """
    runes = ['⚡', '🌙', '🛡️', '❤️', '💀']
    selected = random.choices(runes, k=3)
    
    if '💀' in selected:
        return selected, "💀 РУНА СМЕРТИ - ПОРАЖЕНИЕ", 0.0
    
    unique_count = len(set(selected))
    
    if unique_count == 1:
        return selected, "✨ ТРИ ОДИНАКОВЫЕ РУНЫ", 10.0
    elif unique_count == 2:
        return selected, "🌟 ДВЕ ОДИНАКОВЫЕ РУНЫ", 3.0
    else:
        return selected, "🍀 ВСЕ РАЗНЫЕ - УДАЧА", 2.0
