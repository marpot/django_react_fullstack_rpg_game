from game.services.combat_service import CombatService
from game.services.dice_service import DiceService


class BattleService:
    def __init__(self, seed: int = 1):
        self.combat = CombatService(DiceService(seed=seed))

    def fight(self, attacker, defender):
        rounds = []
        round_index = 0

        # snapshot HP startowych (debug/test-friendly)
        starting_attacker_hp = attacker.hp
        starting_defender_hp = defender.hp

        while attacker.hp > 0 and defender.hp > 0:
            round_index += 1

            result = self.combat.resolve(attacker, defender)

            rounds.append({
                "round": round_index,
                "attacker_hit": result.attacker_hit,
                "defender_hit": result.defender_hit,
                "attacker_damage": result.attacker_damage,
                "defender_damage": result.defender_damage,
                "attacker_hp": attacker.hp,
                "defender_hp": defender.hp,
            })

            if attacker.hp <= 0 or defender.hp <= 0:
                break

        if attacker.hp <= 0 and defender.hp <= 0:
            winner = "draw"
        elif attacker.hp <= 0:
            winner = "defender"
        else:
            winner = "attacker"

        return {
            "rounds": rounds,
            "winner": winner,
            "summary": {
                "attacker_start_hp": starting_attacker_hp,
                "defender_start_hp": starting_defender_hp,
                "rounds_count": round_index,
            }
        }