from hearthbreaker.tags.action import Draw, Damage, Give, Heal
from hearthbreaker.tags.base import Aura, Effect, Battlecry
from hearthbreaker.tags.condition import Adjacent, HasOverload
from hearthbreaker.tags.event import TurnEnded, CardPlayed
from hearthbreaker.tags.selector import MinionSelector, SelfSelector, PlayerSelector, CharacterSelector, BothPlayer, \
    UserPicker
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
        return Minion(2, 4, effects=[Effect(CardPlayed(HasOverload()), ChangeAttack(1), SelfSelector()),
                                     Effect(CardPlayed(HasOverload()), ChangeHealth(1), SelfSelector())])


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
