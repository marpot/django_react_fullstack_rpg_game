from dataclasses import dataclass


@dataclass(frozen=True)
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
        defender_hit, defender_damage = self._attack(defender, attacker)

        # ❌ NIE MUTUJEMY STANU TU
        # HP zmienia ActionProcessor

        winner = self._resolve_winner(attacker, defender)

        return CombatResult(
            attacker_hit=attacker_hit,
            defender_hit=defender_hit,
            attacker_damage=attacker_damage,
            defender_damage=defender_damage,
            winner=winner
        )

    def _resolve_winner(self, attacker, defender):
        if attacker.hp <= 0 and defender.hp <= 0:
            return "draw"
        if defender.hp <= 0:
            return "attacker"
        if attacker.hp <= 0:
            return "defender"
        return None

    def _attack(self, attacker, defender):
        roll = self.dice.roll(20)
        total_attack = roll + attacker.attack_bonus

        hit = total_attack >= defender.defense

        if not hit:
            return False, 0

        raw_damage = self.dice.roll(attacker.damage_die) + attacker.damage_bonus
        mitigated = max(0, raw_damage - getattr(defender, "armor", 0))

        return True, mitigated