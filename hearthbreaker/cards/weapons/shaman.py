from hearthbreaker.cards.base import WeaponCard
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hearthbreaker.game_objects import Weapon
from hearthbreaker.tags.action import Give
from hearthbreaker.tags.base import Buff, Deathrattle
from hearthbreaker.tags.condition import IsType
from hearthbreaker.tags.status import Windfury, ChangeAttack, ChangeHealth
from hearthbreaker.tags.selector import MinionSelector, RandomPicker


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


class Powermace(WeaponCard):
    def __init__(self):
        super().__init__("Powermace", 3, CHARACTER_CLASS.SHAMAN, CARD_RARITY.RARE)

    def create_weapon(self, player):
        return Weapon(3, 2, deathrattle=Deathrattle(Give([Buff(ChangeHealth(2)), Buff(ChangeAttack(2))]),
                                                    MinionSelector(IsType(MINION_TYPE.MECH), picker=RandomPicker())))
