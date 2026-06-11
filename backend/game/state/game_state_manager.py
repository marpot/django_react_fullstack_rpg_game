from dataclasses import dataclass, field
from game.state.runtime.models import Player

@dataclass
class Enemy:
    name: str
    hp: int
    defense: int
    attack_bonus: int
    damage_die: int
    damage_bonus: int

@dataclass
class RoomState:
    name: str
    players: dict[int, Player] = field(default_factory=dict)
    enemies: dict[str, Enemy] = field(default_factory=dict)

class GameStateManager:
    """
    Centralny runtime świata gry (MVP in-memory).
    Trzyma wszystkie roomy i i ch stan.
    """

    def normalize_room_id(self, room_id: str | int) -> str:
        return str(room_id)

    def __init__(self):
        self.rooms: dict[str, RoomState] = {}

    def get_room(self, room_name: str) -> RoomState | None:
        return self.rooms.get(self.normalize_room_id(room_name))

    def get_or_create_room(self, room_name: str) -> RoomState:
        key = self.normalize_room_id(room_name)

        if key not in self.rooms:
            self.rooms[key] = self._create_default_room(key)

        return self.rooms[key]

    def _create_default_room(self, room_name: str) -> RoomState:
        room = RoomState(name=self.normalize_room_id(room_name))

        #TEMPLATE MOCK ENEMY (STARTER)
        room.enemies["goblin"] = Enemy(
            name="goblin",
            hp=30,
            defense=10,
            attack_bonus=2,
            damage_die=6,
            damage_bonus=1
        )

        return room
    
    def get_enemy(self, room_name: str, enemy_name: str):
        room = self.get_or_create_room(self.normalize_room_id(room_name))
        return room.enemies.get(enemy_name)
    
    def get_player(self, room_name: str, user_id: int):
        room = self.get_or_create_room(self.normalize_room_id(room_name))
        player = room.players.get(user_id)
        if player:
            return player
        
        return None
    
    def add_player(self, room_name: str, user_id: int, player: Player):
        room = self.get_or_create_room(self.normalize_room_id(room_name))
        room.players[user_id] = player

    def add_enemy(self, room_name: str, enemy):
        room = self.get_or_create_room(self.normalize_room_id(room_name))
        room.enemies[enemy.name] = enemy