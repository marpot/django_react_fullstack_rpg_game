from dataclasses import dataclass, field

# =========================
# PLAYER (runtime entity)
# =========================
@dataclass
class Player:
    id: int
    name: str
    hp: int
    max_hp: int

    attack_bonus: int
    damage_die: int
    damage_bonus: int
    defense: int


# =========================
# ENEMY (runtime entity)
# =========================
@dataclass
class Enemy:
    id: str
    name: str
    hp: int
    defense: int
    attack_bonus: int
    damage_die: int
    damage_bonus: int


# =========================
# ROOM STATE (runtime container)
# =========================
@dataclass
class RoomState:
    name: str
    players: dict[int, Player] = field(default_factory=dict)
    enemies: dict[str, Enemy] = field(default_factory=dict)
    npcs: dict[str, "NPC"] = field(default_factory=dict)