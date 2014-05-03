__author__ = 'Daniel'

from hsgame.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hsgame.game_objects import MinionCard, Minion, Card


class WaterElemental(MinionCard):
    def __init__(self):
        super().__init__("Water Elemental", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE)

    def create_minion(self, player):
        def did_damage(amount, target):
            target.freeze()

        minion = Minion(3, 6)
        minion.bind("did_damage", did_damage)
        return minion