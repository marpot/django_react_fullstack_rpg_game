from game.state.runtime.models import Player
from game.state.game_state_manager import GameStateManager, Enemy


class GameBootstrap:
    @staticmethod
    def seed_test_world(state: GameStateManager, room: str, participant_id: int):
        room_state = state.get_or_create_room(room)

        if participant_id not in room_state.players:
            room_state.players[participant_id] = Player(
            id=participant_id,
            name=f"player_{participant_id}",
            max_hp=100,
            hp=100,
            attack_bonus=5,
            defense=10,
            damage_die=6,
            damage_bonus=1
        )

        if "goblin" not in room_state.enemies:
            room_state.enemies["goblin"] = Enemy(
                name="goblin",
                hp=30,
                defense=10,
                attack_bonus=2,
                damage_die=6,
                damage_bonus=1
            )