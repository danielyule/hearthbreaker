from hearthbreaker.tags.action import ChangeAttack, Draw, ChangeHealth
from hearthbreaker.tags.base import Aura, Effect
from hearthbreaker.tags.condition import Adjacent, HasOverload
from hearthbreaker.tags.event import TurnEnded, CardPlayed
from hearthbreaker.tags.selector import MinionSelector, SelfSelector, PlayerSelector
import hearthbreaker.targeting
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hearthbreaker.game_objects import MinionCard, Minion
from hearthbreaker.cards.battlecries import deal_three_damage, give_windfury


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
                         targeting_func=hearthbreaker.targeting.find_battlecry_target)

    def create_minion(self, player):
        return Minion(6, 5, battlecry=deal_three_damage)


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
                         targeting_func=hearthbreaker.targeting.find_friendly_minion_battlecry_target)

    def create_minion(self, player):
        return Minion(3, 3, battlecry=give_windfury)
