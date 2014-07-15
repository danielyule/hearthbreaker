from hsgame.constants import CHARACTER_CLASS, CARD_RARITY
from hsgame.game_objects import WeaponCard, Weapon


class AssassinsBlade(WeaponCard):
    def __init__(self):
        super().__init__("Assassin's Blade", 5, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON)

    def create_weapon(self, player):
        weapon = Weapon(3, 4)
        return weapon
