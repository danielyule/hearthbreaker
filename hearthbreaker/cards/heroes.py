from hearthbreaker.cards.base import HeroCard
from hearthbreaker.constants import CHARACTER_CLASS, MINION_TYPE
from hearthbreaker.powers import MagePower, DruidPower, HunterPower, PaladinPower, PriestPower, RoguePower,\
    ShamanPower, WarlockPower, WarriorPower, JaraxxusPower, DieInsect


class Malfurion(HeroCard):
    def __init__(self):
        super().__init__("Malfurion Stormrage", CHARACTER_CLASS.DRUID, 30, DruidPower)


class Rexxar(HeroCard):
    def __init__(self):
        super().__init__("Rexxar", CHARACTER_CLASS.HUNTER, 30, HunterPower)


class Jaina(HeroCard):
    def __init__(self):
        super().__init__("Jaina Proudmoore", CHARACTER_CLASS.MAGE, 30, MagePower)


class Uther(HeroCard):
    def __init__(self):
        super().__init__("Uther the Lightbringer", CHARACTER_CLASS.PALADIN, 30, PaladinPower)


class Anduin(HeroCard):
    def __init__(self):
        super().__init__("Anduin Wrynn", CHARACTER_CLASS.PRIEST, 30, PriestPower)


class Valeera(HeroCard):
    def __init__(self):
        super().__init__("Valeera Sanguinar", CHARACTER_CLASS.ROGUE, 30, RoguePower)


class Thrall(HeroCard):
    def __init__(self):
        super().__init__("Thrall", CHARACTER_CLASS.SHAMAN, 30, ShamanPower)


class Guldan(HeroCard):
    def __init__(self):
        super().__init__("Gul'dan", CHARACTER_CLASS.WARLOCK, 30, WarlockPower)


class Garrosh(HeroCard):
    def __init__(self):
        super().__init__("Garrosh Hellscream", CHARACTER_CLASS.WARRIOR, 30, WarriorPower)


class Jaraxxus(HeroCard):
    def __init__(self):
        super().__init__("Lord Jaraxxus", CHARACTER_CLASS.WARLOCK, 15, JaraxxusPower, MINION_TYPE.DEMON,
                         ref_name="Lord Jarraxus (hero)")


class Ragnaros(HeroCard):
    def __init__(self):
        super().__init__("Ragnaros the Firelord (hero)", CHARACTER_CLASS.ALL, 8, DieInsect)


def hero_for_class(character_class):
    if character_class == CHARACTER_CLASS.DRUID:
        return Malfurion()
    elif character_class == CHARACTER_CLASS.HUNTER:
        return Rexxar()
    elif character_class == CHARACTER_CLASS.MAGE:
        return Jaina()
    elif character_class == CHARACTER_CLASS.PRIEST:
        return Anduin()
    elif character_class == CHARACTER_CLASS.PALADIN:
        return Uther()
    elif character_class == CHARACTER_CLASS.ROGUE:
        return Valeera()
    elif character_class == CHARACTER_CLASS.SHAMAN:
        return Thrall()
    elif character_class == CHARACTER_CLASS.WARLOCK:
        return Guldan()
    elif character_class == CHARACTER_CLASS.WARRIOR:
        return Garrosh()
    else:
        return Jaina()


__hero_lookup = {"Jaina": Jaina,
                 "Malfurion": Malfurion,
                 "Rexxar": Rexxar,
                 "Anduin": Anduin,
                 "Uther": Uther,
                 "Gul'dan": Guldan,
                 "Valeera": Valeera,
                 "Thrall": Thrall,
                 "Garrosh": Garrosh,
                 "Jaraxxus": Jaraxxus,
                 "Ragnaros": Ragnaros,
                 }


def hero_from_name(name):
    return __hero_lookup[name]()
