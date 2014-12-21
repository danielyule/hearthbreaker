import hearthbreaker.cards
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hearthbreaker.tags.action import Freeze, AddCard, Give
from hearthbreaker.tags.aura import ManaAura
from hearthbreaker.tags.base import Effect, Aura, Battlecry
from hearthbreaker.tags.condition import HasSecret
from hearthbreaker.tags.event import SpellCast, DidDamage, TurnEnded
from hearthbreaker.tags.selector import SecretSelector, SpellSelector, PlayerSelector, SelfSelector, TargetSelector
from hearthbreaker.game_objects import MinionCard, Minion
from hearthbreaker.tags.status import ChangeAttack, ChangeHealth, ManaChange


class ManaWyrm(MinionCard):
    def __init__(self):
        super().__init__("Mana Wyrm", 1, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(1, 3, effects=[Effect(SpellCast(), ChangeAttack(1), SelfSelector())])


class SorcerersApprentice(MinionCard):
    def __init__(self):
        super().__init__("Sorcerer's Apprentice", 2, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(3, 2, auras=[Aura(ManaChange(1, 0, SpellSelector()), PlayerSelector())])


class KirinTorMage(MinionCard):
    def __init__(self):
        super().__init__("Kirin Tor Mage", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.RARE,
                         battlecry=Battlecry(Give([ManaAura(100, 0, SecretSelector(), True)]), PlayerSelector()))

    def create_minion(self, player):
        def first_secret_cost_zero(m):
            m.player.add_aura(ManaAura(100, 0, SecretSelector(), True))

        return Minion(4, 3)


class EtherealArcanist(MinionCard):
    def __init__(self):
        super().__init__("Ethereal Arcanist", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(3, 3, effects=[Effect(TurnEnded(HasSecret()), ChangeAttack(2), SelfSelector()),
                                     Effect(TurnEnded(HasSecret()), ChangeHealth(2), SelfSelector())])


class WaterElemental(MinionCard):
    def __init__(self):
        super().__init__("Water Elemental", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(3, 6, effects=[Effect(DidDamage(), Freeze(), TargetSelector())])


class ArchmageAntonidas(MinionCard):
    def __init__(self):
        super().__init__("Archmage Antonidas", 7, CHARACTER_CLASS.MAGE, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(5, 7, effects=[Effect(SpellCast(), AddCard(hearthbreaker.cards.Fireball()), PlayerSelector())])


class Snowchugger(MinionCard):
    def __init__(self):
        super().__init__("Snowchugger", 2, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON, MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(2, 3, effects=[Effect(DidDamage(), Freeze(), TargetSelector())])
