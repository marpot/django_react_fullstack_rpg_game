from chat.models import RoomParticipant
from game.state.runtime.models import Player


class GameStartService:

    def __init__(self, seeder, llm, notifier, state_manager):
        self.seeder = seeder
        self.llm = llm
        self.notifier = notifier
        self.state_manager = state_manager

    def start_game(self, adventure_id, room_id, user_id, adventure=None):

        # 1. seed world (SOURCE OF TRUTH)
        self.seeder.seed_from_adventure(adventure_id, room_id)

        # 1.5 INIT TURN SYSTEM (FIX)
        room_state = self.state_manager.get_or_create_room(room_id)

        participants = list(
            RoomParticipant.objects.filter(room_id=room_id)
        )

        room_state.players = {
            p.id: Player(id=p.id, name=getattr(p, "name", str(p.id)))
            for p in participants
        }

        room_state.turn_order = list(room_state.players.keys())

        if room_state.turn_order:
            room_state.current_player_id = room_state.turn_order[0]
            room_state.current_turn_index = 0

        # 2. LLM world DTO
        adventure_context = {"id": adventure_id}
        if adventure is not None:
            adventure_context["title"] = getattr(adventure, "title", None) or adventure.get("title")
            adventure_context["description"] = getattr(adventure, "description", None) or adventure.get("description")

        world_raw = self.llm.generate_world({"adventure": adventure_context})

        if not isinstance(world_raw, dict):
            world_raw = {
                "intro": "A strange world forms...",
                "situation": "The world is unstable."
            }

        world = {
            "name": world_raw.get("name", "Unknown World"),
            "title": world_raw.get("title", "Unknown World"),
            "description": world_raw.get("description", ""),
            "intro": world_raw.get("intro", ""),
            "lore": {
                "situation": world_raw.get("situation", ""),
            },
            "rules": world_raw.get("rules", {}),
            "seed": world_raw.get("seed", {}),
        }

        # 3. LLM narracja (spin świata)
        intro = self.llm.generate_intro({
            "world": world,
            "adventure_id": adventure_id,
        })

        intro_text = intro.get("text") if isinstance(intro, dict) else None
        if intro_text:
            world["intro"] = intro_text

        # 4. emit JEDEN spójny event
        self.notifier.emit(room_id, {
            "type": "game_started",
            "event": "game_started",
            "payload": {
                "world": world,
                "intro": intro,
                "adventure_id": adventure_id,
                "room_id": room_id,
            },
        })

        return world