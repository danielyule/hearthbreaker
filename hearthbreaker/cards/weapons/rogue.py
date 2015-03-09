from hearthbreaker.cards.base import WeaponCard
from hearthbreaker.game_objects import Weapon
from hearthbreaker.tags.action import Damage
from hearthbreaker.tags.base import Battlecry, Buff
from hearthbreaker.tags.condition import GreaterThan, IsType
from hearthbreaker.tags.selector import CharacterSelector, UserPicker, Count, MinionSelector
from hearthbreaker.tags.status import ChangeAttack
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE


class WickedKnife(WeaponCard):
    def __init__(self):
        super().__init__("Wicked Knife", 1, CHARACTER_CLASS.ROGUE, CARD_RARITY.FREE, False)

    def create_weapon(self, player):
        return Weapon(1, 2)


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


class CogmastersWrench(WeaponCard):
    def __init__(self):
        super().__init__("Cogmaster's Wrench", 3, CHARACTER_CLASS.ROGUE, CARD_RARITY.EPIC)

    def create_weapon(self, player):
        return Weapon(1, 3, buffs=[Buff(ChangeAttack(2), GreaterThan(Count(MinionSelector(IsType(MINION_TYPE.MECH))),
                                                                     value=0))])
