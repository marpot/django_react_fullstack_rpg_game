class EventRules:

    @staticmethod
    def is_event_available(event, player):
        for flag in event.required_flags:
            if flag not in player.flags:
                return False

        for flag in event.blocking_flags:
            if flag in player.flags:
                return False

        req = event.requirements or {}

        if player.level < req.get("min_level", 0):
            return False

        for item in req.get("required_items", []):
            if item not in player.inventory:
                return False

        for skill in req.get("required_skills", []):
            if skill not in player.skills:
                return False

        return True

    @staticmethod
    def is_choice_available(choice, player):
        req = choice.get("requirements", {})

        if player.level < req.get("min_level", 0):
            return False

        for item in req.get("required_items", []):
            if item not in player.inventory:
                return False

        for skill in req.get("required_skills", []):
            if skill not in player.skills:
                return False

        for flag in req.get("required_flags", []):
            if flag not in player.flags:
                return False

        return True