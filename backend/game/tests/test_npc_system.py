import pytest
from game.state.game_state_manager import GameStateManager
from game.npc.npc_models import NPC
from game.npc.npc_service import NPCService
from game.state.seeders.npc_seeder import NPCSeeder

pytestmark = pytest.mark.django_db

# -------------------------
# SPAWN TEST 
# -------------------------
def test_npc_spawn_adds_to_room_state():
    state = GameStateManager()
    state.get_or_create_room("testroom")

    service = NPCService(state)

    npc = NPC(
        id="old_man",
        name="Old Man",
        dialog=["Hello"]
    )

    service.spawn("testroom", npc)

    room = state.get_or_create_room("testroom")

    assert "old_man" in room.npcs


# -------------------------
# SEED TEST
# -------------------------
def test_npc_seed_creates_starter_npcs():
    state = GameStateManager()
    state.get_or_create_room("testroom")

    seeder = NPCSeeder(state)

    seeder.seed("testroom", 1)

    room = state.get_or_create_room("testroom")

    assert "old_man" in room.npcs
    assert "merchant" in room.npcs
    assert len(room.npcs) == 2