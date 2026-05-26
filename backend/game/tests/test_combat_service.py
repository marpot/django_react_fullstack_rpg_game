import pytest
from game.services.combat_service import CombatService
from game.services.dice_service import DiceService

class DummyEntity:
    def __init__(self):
        self.hp = 100
        self.attack_bonus = 5
        self.defense = 10
        self.damage_die = 6
        self.damage_bonus = 2


def test_combat_resolve():
    dice = DiceService(seed=1)
    combat = CombatService(dice)

    attacker = DummyEntity()
    defender = DummyEntity()

    result = combat.resolve(attacker, defender)

    assert isinstance(result.attacker_hit, bool)
    assert isinstance(result.defender_hit, bool)

    assert isinstance(result.attacker_damage, int)
    assert isinstance(result.defender_damage, int)

    assert defender.hp <= 100
    assert defender.hp >= 0

    if result.attacker_hit:
        assert result.attacker_damage > 0
    else:
        assert result.attacker_damage == 0