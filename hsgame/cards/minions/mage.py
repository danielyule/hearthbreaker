__author__ = 'Daniel'

from hsgame.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hsgame.game_objects import MinionCard, Minion, Card


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


class WaterElemental(MinionCard):
    def __init__(self):
        super().__init__("Water Elemental", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE)

    def create_minion(self, player):
        def did_damage(amount, target):
            target.freeze()

        minion = Minion(3, 6)
        minion.bind("did_damage", did_damage)
        return minion