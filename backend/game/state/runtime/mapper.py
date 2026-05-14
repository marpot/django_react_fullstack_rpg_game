from accounts.models import PlayerCharacter
from .models import Player

def to_runtime_player(pc: PlayerCharacter) -> Player:
    return Player(
        id = pc.id,
        name = pc.name,
        hp=pc.health,
        max_hp=pc.max_health,
        attack=pc.strength
    )