import random


class DiceService:
    def __init__(self, seed: int | None = None):
        self.random = random.Random(seed)

    def roll(self, sides:int) -> int:
        return self.random.randint(1, sides)