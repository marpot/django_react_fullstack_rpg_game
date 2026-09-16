from collections.abc import Mapping

from game.core.game_command import GameCommand


class AdventureChoiceService:
    """Suggest commands from the current server-side room state."""

    MAX_CHOICES = 6

    def build_choices(
        self,
        *,
        enemies: Mapping[str, object],
        npcs: Mapping[str, object],
    ) -> list[dict]:
        choices = [self._choice(
            "inspect", None, "Rozejrzyj się",
            "Sprawdź otoczenie i ślady przygody.", "sprawdź otoczenie",
        )]

        seen_enemies = set()
        for enemy in enemies.values():
            target = getattr(enemy, "name", "").lower().strip()
            if not target or target in seen_enemies or getattr(enemy, "hp", 0) <= 0:
                continue
            seen_enemies.add(target)
            choices.append(self._choice(
                "attack", target, f"Atakuj {enemy.name}",
                f"Zaatakuj {enemy.name}.", f"attack {target}",
            ))
            if len(seen_enemies) >= 3:
                break

        for npc_id, npc in npcs.items():
            if not isinstance(npc_id, str) or not npc_id:
                continue
            name = getattr(npc, "name", npc_id)
            choices.append(self._choice(
                "talk", npc_id, f"Porozmawiaj z {name}",
                f"Porozmawiaj z {name}.", f"talk {npc_id}",
            ))
            if len(choices) >= self.MAX_CHOICES:
                break

        return choices

    @staticmethod
    def _choice(action: str, target: str | None, label: str,
                description: str, message: str) -> dict:
        command = GameCommand(action=action, target=target, method=None)
        return {
            "id": f"{action}-{target}" if target else action,
            "label": label,
            "title": label,
            "description": description,
            "message": message,
            "action": command.action,
            "target": command.target,
            "method": command.method,
        }
