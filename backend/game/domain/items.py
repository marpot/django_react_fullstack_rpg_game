from dataclasses import dataclass

@dataclass
class Item:
    name: str
    attack_bonus: int = 0
    defense_bonus: int = 0
    armor_bonus: int = 0
    crit_bonus: float = 0.0