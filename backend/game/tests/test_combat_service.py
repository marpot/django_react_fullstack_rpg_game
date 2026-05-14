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

    assert result.attacker_hit is not None
    assert isinstance(result.attacker_damage, int)
    assert defender.hp <= 100