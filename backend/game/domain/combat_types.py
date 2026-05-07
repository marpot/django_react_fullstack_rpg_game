from game.domain.stats import Stats

def apply_items(base: Stats, items: list):

    attack_bonus = sum(i.attack_bonus for i in items)
    defense_bonus = sum(i.defense_bonus for i in items)
    armor_bonus = sum(i.armor_bonus for i in items)
    crit_bonus = sum(i.crit_bonus for i in items)

    return Stats(
        level=base.level,
        hp=base.hp,
        max_hp=base.max_hp,

        attack=base.attack + attack_bonus,
        defense=base.defense + defense_bonus,
        strength=base.strength,
        agility=base.agility,

        armor=base.armor + armor_bonus,
        crit_chance=base.crit_chance + crit_bonus,
    )