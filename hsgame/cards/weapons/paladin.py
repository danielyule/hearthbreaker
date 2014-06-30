from hsgame.constants import CHARACTER_CLASS, CARD_RARITY
from hsgame.game_objects import WeaponCard, Weapon

__author__ = 'Markus'


class LightsJustice(WeaponCard):
    def __init__(self):
        super().__init__("Light's Justice", 1, CHARACTER_CLASS.PALADIN, CARD_RARITY.FREE)

    def create_weapon(self, player):
        weapon = Weapon(1, 4)
        return weapon
