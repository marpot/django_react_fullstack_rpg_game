from game.state.runtime.models import Player, Enemy

class EntityResolver:
    def __init__(self, state_manager):
        self.state_manager = state_manager

    def resolve_player(self, room_name: str, user_id: int):
        room = self.state_manager.get_room(room_name)
        if not room:
            return None

        player = room.players.get(user_id)
        return self._normalize_player(player)

    def resolve_enemy(self, room_name: str, enemy_name: str):
        room = self.state_manager.get_room(room_name)

        # 1. runtime cache
        if room and enemy_name in room.enemies:
            return room.enemies[enemy_name]

        # 2. ORM fallback
        from world.models import Enemy

        enemy = Enemy.objects.filter(name=enemy_name).first()
        if not enemy:
            return None

        # runtime object (prosty mapping)
        return type("EnemyRuntime", (), {
            "id": enemy.id,
            "name": enemy.name,
            "hp": enemy.hp,
            "defense": enemy.defense,
            "attack_bonus": enemy.attack_bonus,
            "damage_die": enemy.damage_die,
            "damage_bonus": enemy.damage_bonus,
        })()

        return room.enemies.get(enemy_name)

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