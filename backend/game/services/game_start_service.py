class GameStartService:

    def __init__(self, seeder, llm, notifier):
        self.seeder = seeder
        self.llm = llm
        self.notifier = notifier

    def start_game(self, adventure_id, room_id, user_id):

        # 1. seed world (SOURCE OF TRUTH)
        room = self.seeder.seed_from_adventure(adventure_id, room_id)

        # 2. LLM narracja (spin świata)
        intro = self.llm.generate_intro({
            "world": room.world,
            "adventure_id": adventure_id,
        })

        # 3. emit JEDEN spójny event
        self.notifier.emit(room_id, {
            "type": "game_event",
            "event": "world_start",
            "payload": {
                "world": room.world,
                "intro": intro,
            },
        })

        return room