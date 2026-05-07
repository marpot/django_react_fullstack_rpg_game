from dataclasses import dataclass
from game.services.dice_service import DiceService


@dataclass(frozen=True)  #frozen=True = obiekt jest niemutowalny - wynik walki w tym przypadku
class CombatResult:
    attacker_hit: bool
    defender_hit: bool
    attacker_damage: int
    defender_damage: int
    winner: str | None


class CombatService:
    def __init__(self, dice_service):
        self.dice = dice_service

    def resolve(self, attacker, defender) -> CombatResult:
        attacker_hit, attacker_damage = self._attack(attacker, defender)
        defender_hit, defender_damage = False, 0
        winner = None

        if attacker.hp <= 0:
            return CombatResult(
                attacker_hit=attacker_hit,
                defender_hit=False,
                attacker_damage=attacker_damage,
                defender_damage=0,
                winner="defender"
            )

        if defender.hp > 0:
            defender_hit, defender_damage = self._attack(defender, attacker)

        if defender.hp <= 0 and attacker.hp > 0:
            winner = "attacker"
        elif attacker.hp <= 0:
            winner = "defender"

        return CombatResult(
            attacker_hit=attacker_hit,
            defender_hit=defender_hit,
            attacker_damage=attacker_damage,
            defender_damage=defender_damage,
            winner=winner
        )

    def _attack(self, attacker, defender):
        roll = self.dice.roll(20)
        total_attack = roll + attacker.attack_bonus

        if total_attack >= defender.defense:
            damage = self.dice.roll(attacker.damage_die) + attacker.damage_bonus
            defender.hp -= damage
            return True, damage

        return False, 0