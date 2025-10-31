import random
from typing import List, Tuple


class DiceRoller:
    @staticmethod
    def roll(dice_expression: str) -> Tuple[int, List[int]]:
        """Simple dice expression parser, e.g. '2d6+3'."""
        expression = dice_expression.lower().replace(" ", "")
        modifier = 0
        if '+' in expression:
            expression, mod_str = expression.split('+', 1)
            modifier = int(mod_str)
        elif '-' in expression:
            expression, mod_str = expression.split('-', 1)
            modifier = -int(mod_str)

        count, sides = expression.split('d')
        count = int(count or 1)
        sides = int(sides)

        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls) + modifier
        return total, rolls
