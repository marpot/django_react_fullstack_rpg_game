from dataclasses import dataclass

@dataclass
class Stats:
    level: int
    hp: int
    max_hp: int

    attack: int
    defense: int
    strength: int
    agility: int

    armor: int = 0
    crit_chance: float = 0.05 #5%
