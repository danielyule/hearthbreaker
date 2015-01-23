from hearthbreaker.tags.action import Draw, Damage, Give, Heal, ChangeTarget
from hearthbreaker.tags.base import Aura, Effect, Battlecry
from hearthbreaker.tags.condition import Adjacent, HasOverload, IsType, OneIn, NotCurrentTarget
from hearthbreaker.tags.event import TurnEnded, CardPlayed, MinionDied, Attack
from hearthbreaker.tags.selector import MinionSelector, PlayerSelector, HeroSelector, CharacterSelector, BothPlayer, \
    UserPicker, SelfSelector, RandomPicker, EnemyPlayer
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hearthbreaker.game_objects import MinionCard, Minion
from hearthbreaker.tags.status import ChangeAttack, ChangeHealth, Windfury


class AlAkirTheWindlord(MinionCard):
    def __init__(self):
        super().__init__("Al'Akir the Windlord", 8, CHARACTER_CLASS.SHAMAN, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(3, 5, windfury=True, charge=True, divine_shield=True, taunt=True)


class DustDevil(MinionCard):
    def __init__(self):
        super().__init__("Dust Devil", 1, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON, overload=2)

    def create_minion(self, player):
        return Minion(3, 1, windfury=True)


class EarthElemental(MinionCard):
    def __init__(self):
        super().__init__("Earth Elemental", 5, CHARACTER_CLASS.SHAMAN, CARD_RARITY.EPIC, overload=3)

    def create_minion(self, player):
        return Minion(7, 8, taunt=True)


class FireElemental(MinionCard):
    def __init__(self):
        super().__init__("Fire Elemental", 6, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Damage(3), CharacterSelector(players=BothPlayer(), picker=UserPicker())))

    def create_minion(self, player):
        return Minion(6, 5)


class FlametongueTotem(MinionCard):
    def __init__(self):
        super().__init__("Flametongue Totem", 2, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON, MINION_TYPE.TOTEM)

    def create_minion(self, player):
        return Minion(0, 3, auras=[Aura(ChangeAttack(2), MinionSelector(Adjacent()))])


class ManaTideTotem(MinionCard):
    def __init__(self):
        super().__init__("Mana Tide Totem", 3, CHARACTER_CLASS.SHAMAN, CARD_RARITY.RARE, MINION_TYPE.TOTEM)

    def create_minion(self, player):
        return Minion(0, 3, effects=[Effect(TurnEnded(), Draw(), PlayerSelector())])


class UnboundElemental(MinionCard):
    def __init__(self):
        super().__init__("Unbound Elemental", 3, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(2, 4, effects=[Effect(CardPlayed(HasOverload()), Give(ChangeAttack(1)), SelfSelector()),
                                     Effect(CardPlayed(HasOverload()), Give(ChangeHealth(1)), SelfSelector())])


class Windspeaker(MinionCard):
    def __init__(self):
        super().__init__("Windspeaker", 4, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Give(Windfury()), MinionSelector(picker=UserPicker())))

    def create_minion(self, player):
        return Minion(3, 3)


class HealingTotem(MinionCard):
    def __init__(self):
        super().__init__("Healing Totem", 1, CHARACTER_CLASS.SHAMAN, CARD_RARITY.SPECIAL, MINION_TYPE.TOTEM)

    def create_minion(self, player):
        return Minion(0, 2, effects=[Effect(TurnEnded(), Heal(1), MinionSelector(condition=None))])


class SearingTotem(MinionCard):
    def __init__(self):
        super().__init__("Searing Totem", 1, CHARACTER_CLASS.SHAMAN, CARD_RARITY.SPECIAL, MINION_TYPE.TOTEM)

    def create_minion(self, player):
        return Minion(1, 1)


class StoneclawTotem(MinionCard):
    def __init__(self):
        super().__init__("Stoneclaw Totem", 1, CHARACTER_CLASS.SHAMAN, CARD_RARITY.SPECIAL, MINION_TYPE.TOTEM)

    def create_minion(self, player):
        return Minion(0, 2, taunt=True)


class WrathOfAirTotem(MinionCard):
    def __init__(self):
        super().__init__("Wrath of Air Totem", 1, CHARACTER_CLASS.SHAMAN, CARD_RARITY.SPECIAL, MINION_TYPE.TOTEM)

    def create_minion(self, player):
        return Minion(0, 2, spell_damage=1)


class SpiritWolf(MinionCard):
    def __init__(self):
        super().__init__("Spirit Wolf", 2, CHARACTER_CLASS.SHAMAN, CARD_RARITY.SPECIAL)

    def create_minion(self, p):
        return Minion(2, 3, taunt=True)


class VitalityTotem(MinionCard):
    def __init__(self):
        super().__init__("Vitality Totem", 2, CHARACTER_CLASS.SHAMAN, CARD_RARITY.RARE, MINION_TYPE.TOTEM)

    def create_minion(self, player):
        return Minion(0, 3, effects=[Effect(TurnEnded(), Heal(4), HeroSelector())])


class SiltfinSpiritwalker(MinionCard):
    def __init__(self):
        super().__init__("Siltfin Spiritwalker", 4, CHARACTER_CLASS.SHAMAN, CARD_RARITY.EPIC, MINION_TYPE.MURLOC,
                         overload=1)

    def create_minion(self, player):
        return Minion(2, 5, effects=[Effect(MinionDied(IsType(MINION_TYPE.MURLOC)), Draw(), PlayerSelector())])


class WhirlingZapomatic(MinionCard):
    def __init__(self):
        super().__init__("Whirling Zap-o-matic", 2, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON, MINION_TYPE.MECH)

    def create_minion(self, p):
        return Minion(3, 2, windfury=True)


class DunemaulShaman(MinionCard):
    def __init__(self):
        super().__init__("Dunemaul Shaman", 4, CHARACTER_CLASS.SHAMAN, CARD_RARITY.RARE, overload=1)

    def create_minion(self, player):
        return Minion(5, 4, windfury=True, effects=[Effect(Attack(),
                                                           ChangeTarget(CharacterSelector(NotCurrentTarget(),
                                                                                          EnemyPlayer(),
                                                                                          RandomPicker())),
                                                           SelfSelector(), OneIn(2))])
