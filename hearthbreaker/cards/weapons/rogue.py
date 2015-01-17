from hearthbreaker.tags.action import Damage
from hearthbreaker.tags.base import Battlecry
from hearthbreaker.tags.selector import CharacterSelector, UserPicker
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.game_objects import WeaponCard, Weapon


class AssassinsBlade(WeaponCard):
    def __init__(self):
        super().__init__("Assassin's Blade", 5, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON)

    def create_weapon(self, player):
        return Weapon(3, 4)


class PerditionsBlade(WeaponCard):
    def __init__(self):
        super().__init__("Perdition's Blade", 3, CHARACTER_CLASS.ROGUE, CARD_RARITY.RARE,
                         battlecry=Battlecry(Damage(1), CharacterSelector(None, picker=UserPicker())),
                         combo=Battlecry(Damage(2), CharacterSelector(None, picker=UserPicker())))

    def create_weapon(self, player):
        return Weapon(2, 2)
