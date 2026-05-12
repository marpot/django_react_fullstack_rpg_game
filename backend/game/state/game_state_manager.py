from dataclasses import dataclass, field

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
    players: dict = field(default_factory=dict)
    enemies: dict = field(default_factory=dict)

class GameStateManager:
    """
    Centralny runtime świata gry (MVP in-memory).
    Trzyma wszystkie roomy i i ch stan.
    """

    def __init__(self):
        self.rooms: dict[str, RoomState] = {}

    def get_or_create_room(self, room_name: str) -> RoomState:
        if room_name not in self.rooms:
            self.rooms[room_name] = self._create_default_room(room_name)

        return self.rooms[room_name]

    def _create_default_room(self, room_name: str) -> RoomState:
        room = RoomState(name=room_name)

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
        room = self.get_or_create_room(room_name)
        return room.enemies.get(enemy_name)
    
    def get_player(self, room_name: str, user_id: int):
        room = self.get_or_create_room(room_name)
        return room.players.get(user_id)
    
    def add_player(self, room_name: str, user_id: int, player_obj):
        room = self.get_or_create_room(room_name)
        room.players[user_id] = player_obj