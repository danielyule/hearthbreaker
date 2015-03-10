from hearthbreaker.cards.base import WeaponCard
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.game_objects import Weapon


class BloodFury(WeaponCard):
    def __init__(self):
        super().__init__("Blood Fury", 3, CHARACTER_CLASS.WARLOCK, CARD_RARITY.RARE, False)

    def create_weapon(self, player):
        return Weapon(3, 8)
