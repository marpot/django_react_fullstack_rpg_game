from chat.models import RoomParticipant
from game.state.runtime.runtime_player_service import RuntimePlayerService


class GameStartService:

    def __init__(self, seeder, llm, notifier, state_manager):
        self.seeder = seeder
        self.llm = llm
        self.notifier = notifier
        self.state_manager = state_manager

    def start_game(self, adventure_id, room_id, adventure=None):
        with self.state_manager.start_lock:
            room_state = self.state_manager.get_or_create_room(room_id)

            if room_state.started and room_state.world is not None:
                return room_state.world

            # 1. seed world (SOURCE OF TRUTH)
            self.seeder.seed_from_adventure(adventure_id, room_id)

            participants = list(
                RoomParticipant.objects.filter(room_id=room_id)
                .select_related("user", "character")
                .order_by("id")
            )

            room_state.players = {}

            runtime_player_service = RuntimePlayerService(self.state_manager)

            for participant in participants:
                runtime_player_service.get_or_create(
                    room_state,
                    participant.id,
                )

            room_state.turn_order = list(room_state.players.keys())
            room_state.player_histories = {
                participant_id: [] for participant_id in room_state.turn_order
            }

            if room_state.turn_order:
                room_state.current_player_id = room_state.turn_order[0]
                room_state.current_turn_index = 0
            else:
                room_state.current_player_id = None
                room_state.current_turn_index = 0

            # 2. LLM world DTO
            adventure_context = {"id": adventure_id}
            if adventure is not None:
                if isinstance(adventure, dict):
                    adventure_context.update({
                        "title": adventure.get("title"),
                        "description": adventure.get("description"),
                    })
                else:
                    adventure_context.update({
                        "title": getattr(adventure, "title", None),
                        "description": getattr(adventure, "description", None),
                    })

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

            room_state.world = world
            room_state.adventure_id = adventure_id
            room_state.started = True

            turn_state = self.state_manager.build_turn_state(room_state)
            game_state = self.state_manager.build_game_state(room_state)

            # 4. emit JEDEN spójny event
            self.notifier.emit(room_id, {
                "type": "game_started",
                "event": "game_started",
                "payload": {
                    "world": world,
                    "intro": intro,
                    "adventure_id": adventure_id,
                    "room_id": room_id,
                    "turn_state": turn_state,
                    "game_state": game_state,
                },
            })

            return world
