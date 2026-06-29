from game.state.runtime.models import Player, Enemy as RuntimeEnemy

PL_MAP = {
    "goblina": "goblin",
    "wilka": "wolf",
    "bandytę": "bandit",
    "bandyta": "bandit",
}

class EntityResolver:
    def __init__(self, state_manager):
        self.state_manager = state_manager

    def _get_room(self, room_name: str):
        if hasattr(self.state_manager, "get_or_create_room"):
            return self.state_manager.get_or_create_room(room_name)

        if hasattr(self.state_manager, "get_room"):
            return self.state_manager.get_room(room_name)

        return None

    def resolve_player(self, room_name: str, user_id: int):
        room = self.state_manager.get_or_create_room(room_name)

        player = room.players.get(user_id) or room.players.get(str(user_id))

        if player:
            return self._normalize_player(player)

        return None

    def resolve_enemy(self, room_name: str, enemy_name: str):
        room = self.state_manager.get_or_create_room(room_name)

        if isinstance(enemy_name, dict):
            enemy_name = enemy_name.get("name") or enemy_name.get("id")

        if not isinstance(enemy_name, str):
            return None

        # ✔ FIX: normalizacja językowa
        enemy_name = enemy_name.lower().strip()
        enemy_name = PL_MAP.get(enemy_name, enemy_name)

        enemy = room.enemies.get(enemy_name)

        if enemy is None:
            for e in getattr(room, "enemies", {}).values():
                if getattr(e, "name", "").lower() == enemy_name:
                    enemy = e
                    break

        if enemy is None:
            return None

        return RuntimeEnemy(
            id=getattr(enemy, "id", enemy.name),
            name=enemy.name,
            hp=enemy.hp,
            defense=enemy.defense,
            attack_bonus=enemy.attack_bonus,
            damage_die=enemy.damage_die,
            damage_bonus=enemy.damage_bonus,
        )

    def _normalize_player(self, player):
        if player is None:
            return None

        return Player(
            id=player.id,
            name=player.name,
            hp=player.hp,
            max_hp=player.max_hp,
            attack_bonus=player.attack_bonus,
            damage_die=player.damage_die,
            damage_bonus=player.damage_bonus,
            defense=player.defense,
        )