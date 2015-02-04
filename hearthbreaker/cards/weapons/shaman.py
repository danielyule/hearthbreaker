from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.game_objects import WeaponCard, Weapon
from hearthbreaker.tags.base import Buff
from hearthbreaker.tags.status import Windfury


class Doomhammer(WeaponCard):
    def __init__(self):
        super().__init__("Doomhammer", 5, CHARACTER_CLASS.SHAMAN, CARD_RARITY.EPIC, overload=2)

    def create_weapon(self, player):
        return Weapon(2, 8, buffs=[Buff(Windfury())])


class StormforgedAxe(WeaponCard):
    def __init__(self):
        super().__init__("Stormforged Axe", 2, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON, overload=1)

    def create_weapon(self, player):
        return Weapon(2, 3)
