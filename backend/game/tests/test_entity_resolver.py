import pytest

from game.state.resolver.entity_resolver import EntityResolver
from game.state.runtime.models import Player, Enemy

# -------------------------
# FAKE STATE (bez Django)
# -------------------------

class FakeRoom:
    def __init__(self):
        self.players = {}
        self.enemies = {}


class FakeStateManager:
    def __init__(self):
        self.rooms = {}

    def create_room(self, name):
        self.rooms[name] = FakeRoom()

    def get_room(self, name):
        return self.rooms.get(name)


# -------------------------
# TESTS
# -------------------------

def test_resolve_player_success():
    state = FakeStateManager()
    state.create_room("testroom")

    room = state.get_room("testroom")
    room.players[1] = Player(
        id=1,
        name='hero',
        hp=100,
        max_hp=100,
        attack_bonus=0,
        damage_die=6,
        damage_bonus=0,
        defense=0
    )

    resolver = EntityResolver(state)

    result = resolver.resolve_player("testroom", 1)

    assert result.id == 1


def test_resolve_player_missing_room():
    state = FakeStateManager()
    resolver = EntityResolver(state)

    result = resolver.resolve_player("missing", 1)

    assert result is None


def test_resolve_enemy_success():
    state = FakeStateManager()
    state.create_room("testroom")

    room = state.get_room("testroom")
    room.enemies["goblin"] = Enemy(
        id="goblin",
        name="goblin",
        hp=30,
        defense=2,
        attack_bonus=1,
        damage_die=6,
        damage_bonus=1,
    )

    resolver = EntityResolver(state)

    result = resolver.resolve_enemy("testroom", "goblin")

    assert result.name == "goblin"


def test_resolve_enemy_missing():
    state = FakeStateManager()
    state.create_room("testroom")

    resolver = EntityResolver(state)

    result = resolver.resolve_enemy("testroom", "dragon")

    assert result is None