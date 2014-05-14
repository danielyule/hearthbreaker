import hsgame.cards

__author__ = 'Daniel'

from hsgame.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hsgame.game_objects import MinionCard, Minion, SecretCard


class ManaWyrm(MinionCard):
    def __init__(self):
        super().__init__("Mana Wyrm", 1, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def increase_attack(card):
            minion.increase_attack(1)
        minion = Minion(1, 3)
        player.bind("spell_cast", increase_attack)
        minion.bind_once("silenced", lambda: player.unbind("spell_cast", increase_attack))
        return minion


class SorcerersApprentice(MinionCard):
    def __init__(self):
        super().__init__("Sorcerer's Apprentice", 2, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def create_minion(self, player):
        class Filter:
            def __init__(self):
                self.amount = 1
                self.filter = lambda c: c.is_spell()
                self.min = 0

        filter = Filter()
        minion = Minion(3, 2)
        minion.bind_once("silence", lambda: player.mana_filters.remove(filter))
        minion.bind_once("died", lambda x: player.mana_filters.remove(filter))
        player.mana_filters.append(filter)
        return minion


class KirinTorMage(MinionCard):
    def __init__(self):
        super().__init__("Kirin Tor Mage", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.RARE)

    def create_minion(self, player):
        class Filter:
            def __init__(self):
                self.amount = 3
                self.filter = lambda c: type(c) in SecretCard.__subclasses__()
                self.min = 0

        def card_used(card):
            if type(card) in SecretCard.__subclasses__():
                player.unbind("card_used", card_used)
                player.unbind("turn_ended", turn_ended)
                player.mana_filters.remove(filter)

        def turn_ended():
            player.unbind("card_used", card_used)
            player.mana_filters.remove(filter)

        filter = Filter()
        minion = Minion(4, 3)
        player.bind("card_used", card_used)
        player.bind_once("turn_ended", turn_ended)
        player.mana_filters.append(filter)

        return minion


class WaterElemental(MinionCard):
    def __init__(self):
        super().__init__("Water Elemental", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE)

    def create_minion(self, player):
        def did_damage(amount, target):
            target.freeze()

        minion = Minion(3, 6)
        minion.bind("did_damage", did_damage)
        return minion