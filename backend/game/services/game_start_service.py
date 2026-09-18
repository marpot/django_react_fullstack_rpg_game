from chat.models import RoomParticipant
from game.core.choice_service import AdventureChoiceService
from game.domain.adventure_definition import (
    build_adventure_definition,
    build_cienie_eldorii_definition,
)
from game.state.seeders.npc_seeder import NPCSeeder
from game.state.runtime.runtime_player_service import RuntimePlayerService
from world.models import Adventure


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

            try:
                adventure_record = (
                    adventure
                    if isinstance(adventure, Adventure)
                    else Adventure.objects.get(pk=adventure_id)
                )
            except Adventure.DoesNotExist:
                adventure_record = None

            definition = None

            if adventure_record is not None:
                builder = (
                    build_cienie_eldorii_definition
                    if adventure_record.title == "Cienie Eldorii"
                    else build_adventure_definition
                )
                definition = builder(adventure_record)

            # AdventureDefinition defines the canonical starting location.
            # Generic/legacy adventures may not define entity placement yet,
            # so their previous placement behaviour is kept as a fallback.
            location_id = (
                str(definition.start_location_id)
                if definition is not None
                and definition.start_location_id is not None
                else "start"
            )

            next_location_id = (
                str(definition.locations[1].id)
                if definition is not None
                and len(definition.locations) > 1
                else location_id
            )

            enemy_definitions = (
                {enemy.id: enemy for enemy in definition.enemies}
                if definition is not None
                else {}
            )

            for enemy_id, enemy in room_state.enemies.items():
                enemy_definition = enemy_definitions.get(enemy_id)

                enemy.location = (
                    str(enemy_definition.location_id)
                    if enemy_definition is not None
                    and enemy_definition.location_id is not None
                    else next_location_id
                )

            room_state.npcs = {}
            NPCSeeder(self.state_manager).seed(room_id, adventure_id)

            npc_definitions = (
                {npc.id: npc for npc in definition.npcs}
                if definition is not None
                else {}
            )

            for index, (npc_id, npc) in enumerate(room_state.npcs.items()):
                npc_definition = npc_definitions.get(npc_id)

                npc.location = (
                    str(npc_definition.location_id)
                    if npc_definition is not None
                    and npc_definition.location_id is not None
                    else location_id if index == 0 else next_location_id
                )

            participants = list(
                RoomParticipant.objects.filter(room_id=room_id)
                .select_related("user", "character")
                .order_by("id")
            )

            room_state.players = {}
            room_state.ai_participants = {
                participant.id for participant in participants if participant.is_ai
            }

            runtime_player_service = RuntimePlayerService(self.state_manager)

            for participant in participants:
                player = runtime_player_service.get_or_create(
                    room_state,
                    participant.id,
                )

                if player is not None:
                    player.location = location_id

            room_state.turn_order = list(room_state.players.keys())
            room_state.player_histories = {
                participant_id: []
                for participant_id in room_state.turn_order
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
                    adventure_context.update(
                        {
                            "title": adventure.get("title"),
                            "description": adventure.get("description"),
                        }
                    )
                else:
                    adventure_context.update(
                        {
                            "title": getattr(adventure, "title", None),
                            "description": getattr(adventure, "description", None),
                        }
                    )

            world_raw = self.llm.generate_world(
                {"adventure": adventure_context}
            )

            if not isinstance(world_raw, dict):
                world_raw = {
                    "intro": "A strange world forms...",
                    "situation": "The world is unstable.",
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
            intro = self.llm.generate_intro(
                {
                    "world": world,
                    "adventure_id": adventure_id,
                }
            )

            intro_text = (
                intro.get("text")
                if isinstance(intro, dict)
                else None
            )

            if intro_text:
                world["intro"] = intro_text

            room_state.world = world
            room_state.adventure_id = adventure_id
            room_state.started = True

            turn_state = self.state_manager.build_turn_state(room_state)
            game_state = self.state_manager.build_game_state(room_state)

            first_player = room_state.players.get(
                room_state.current_player_id
            )

            choices = (
                AdventureChoiceService().build_choices(
                    enemies=self.state_manager.visible_enemies(
                        room_state,
                        first_player,
                    ),
                    npcs=self.state_manager.visible_npcs(
                        room_state,
                        first_player,
                    ),
                    exits=self.state_manager.get_exits(
                        room_state,
                        first_player,
                    ),
                )
                if first_player
                else []
            )

            # 4. emit JEDEN spójny event
            self.notifier.emit(
                room_id,
                {
                    "type": "game_started",
                    "event": "game_started",
                    "payload": {
                        "world": world,
                        "intro": intro,
                        "adventure_id": adventure_id,
                        "room_id": room_id,
                        "turn_state": turn_state,
                        "game_state": game_state,
                        "choices": choices,
                    },
                },
            )

            return world
