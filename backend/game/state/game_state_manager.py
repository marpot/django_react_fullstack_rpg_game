from dataclasses import asdict, dataclass, field
from threading import RLock
from typing import List, Optional, Literal
from game.state.runtime.models import Player

@dataclass
class Enemy:
    name: str
    hp: int
    defense: int
    attack_bonus: int
    damage_die: int
    damage_bonus: int
    location: str = "start"

@dataclass
class NPC:
    id: str
    name: str
    dialog: List[str] = field(default_factory=list)
    state: str = "idle"
    quest_state: str | None = None
    location: str = "start"


@dataclass
class QuestState:
    """Minimalny, deterministyczny stan postępu questa w runtime pokoju."""

    status: Literal["not_started", "active", "completed"] = "not_started"
    stage: str | None = None
    objective: str | None = None
    flags: dict[str, bool] = field(default_factory=dict)
    completed: bool = False

@dataclass
class RoomState:
    name: str
    players: dict[int, Player] = field(default_factory=dict)
    enemies: dict[str, Enemy] = field(default_factory=dict)
    npcs: dict[str, NPC] = field(default_factory=dict)
    turn_order: list[int] = field(default_factory=list)
    current_player_id: int | None = None
    current_turn_index: int = 0
    player_histories: dict[int, list[dict]] = field(default_factory=dict)
    world: dict | None = None
    adventure_id: int | None = None
    quest: QuestState = field(default_factory=QuestState)
    adventure_completed: bool = False
    started: bool = False


class GameStateManager:
    """
    Centralny runtime świata gry (MVP in-memory).
    Trzyma wszystkie roomy i ich stan.
    """

    def normalize_room_id(self, room_id: str | int) -> str:
        return str(room_id)

    def __init__(self):
        self.rooms: dict[str, RoomState] = {}
        self.start_lock = RLock()

    def get_room(self, room_name: str) -> RoomState | None:
        return self.rooms.get(self.normalize_room_id(room_name))

    def get_or_create_room(self, room_name: str) -> RoomState:
        key = self.normalize_room_id(room_name)

        if key not in self.rooms:
            self.rooms[key] = self._create_default_room(key)

        return self.rooms[key]

    def get_location(self, room: RoomState, player: Player):
        if room.adventure_id is None:
            return None
        from world.models import Location

        return Location.objects.filter(
            adventure_id=room.adventure_id, pk=player.location
        ).first() if str(player.location).isdigit() else None

    def get_exits(self, room: RoomState, player: Player):
        location = self.get_location(room, player)
        if location is None:
            return []
        return list(
            location.choices.filter(next_location__adventure_id=room.adventure_id)
            .select_related("next_location")
            .order_by("id")
        )

    def visible_enemies(self, room: RoomState, player: Player):
        return {
            key: enemy for key, enemy in room.enemies.items()
            if getattr(enemy, "location", "start") == player.location
            and enemy.hp > 0
        }

    def visible_npcs(self, room: RoomState, player: Player):
        return {
            key: npc for key, npc in room.npcs.items()
            if getattr(npc, "location", "start") == player.location
        }

    def build_turn_state(
        self,
        room: RoomState,
        participant_id: int | None = None,
    ) -> dict:
        return {
            "current_player_id": room.current_player_id,
            "current_turn_index": room.current_turn_index,
            "turn_order": list(room.turn_order),
            "is_your_turn": (
                room.current_player_id == participant_id
                if participant_id is not None
                else None
            ),
            "history": (
                room.player_histories.get(participant_id, [])
                if participant_id is not None
                else []
            ),
        }

    def build_game_state(self, room: RoomState) -> dict:
        return {
            "players": {
                str(participant_id): asdict(player)
                for participant_id, player in room.players.items()
            },
            "enemies": {
                enemy_id: asdict(enemy)
                for enemy_id, enemy in room.enemies.items()
            },
            "npcs": {
                npc_id: asdict(npc)
                for npc_id, npc in room.npcs.items()
            },
            "quest": asdict(room.quest),
            "adventure_completed": room.adventure_completed,
            "player_histories": {
                str(participant_id): history
                for participant_id, history in room.player_histories.items()
            },
        }

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
    
    def get_player(self, room_name: str, participant_id: int):
        room = self.get_or_create_room(self.normalize_room_id(room_name))
        player = room.players.get(participant_id)
        if player:
            return player
        
        return None
    
    def add_player(self, room_name: str, participant_id: int, player: Player):
        room = self.get_or_create_room(self.normalize_room_id(room_name))
        room.players[participant_id] = player

    def add_enemy(self, room_name: str, enemy):
        room = self.get_or_create_room(self.normalize_room_id(room_name))
        room.enemies[enemy.name] = enemy

    def add_npc(self, room_name: str, npc: NPC):
        room = self.get_or_create_room(self.normalize_room_id(room_name))
        room.npcs[npc.id] = npc
