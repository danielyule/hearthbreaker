from hearthbreaker.cards.base import WeaponCard
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.game_objects import Weapon
from hearthbreaker.tags.action import Damage, IncreaseDurability, ChangeTarget, Give, IncreaseWeaponAttack
from hearthbreaker.tags.base import Deathrattle, Effect, ActionTag, BuffUntil
from hearthbreaker.tags.condition import NotCurrentTarget, OneIn, OpponentMinionCountIsGreaterThan, And, \
    IsHero, TargetIsMinion
from hearthbreaker.tags.event import CharacterAttack, AttackCompleted
from hearthbreaker.tags.selector import MinionSelector, BothPlayer, HeroSelector, CharacterSelector, EnemyPlayer, \
    RandomPicker, WeaponSelector
from hearthbreaker.tags.status import ChangeAttack


class FieryWarAxe(WeaponCard):
    def __init__(self):
        super().__init__("Fiery War Axe", 2, CHARACTER_CLASS.WARRIOR, CARD_RARITY.FREE)

    def create_weapon(self, player):
        return Weapon(3, 2)


class ArcaniteReaper(WeaponCard):
    def __init__(self):
        super().__init__("Arcanite Reaper", 5, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON)

    def create_weapon(self, player):
        return Weapon(5, 2)


class Gorehowl(WeaponCard):
    def __init__(self):
        super().__init__("Gorehowl", 7, CHARACTER_CLASS.WARRIOR, CARD_RARITY.EPIC)

    def create_weapon(self, player):
        return Weapon(7, 1, effects=[Effect(CharacterAttack(And(IsHero(), TargetIsMinion())),
                                            [ActionTag(IncreaseDurability(), WeaponSelector()),
                                             ActionTag(IncreaseWeaponAttack(-1), WeaponSelector()),
                                             ActionTag(Give(BuffUntil(ChangeAttack(1), AttackCompleted())),
                                                       HeroSelector())])])


class HeavyAxe(WeaponCard):
    def __init__(self):
        super().__init__("Heavy Axe", 1, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON, False)

    def create_weapon(self, player):
        return Weapon(1, 3)


class DeathsBite(WeaponCard):
    def __init__(self):
        super().__init__("Death's Bite", 4, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON)

    def create_weapon(self, player):
        return Weapon(4, 2, deathrattle=Deathrattle(Damage(1), MinionSelector(players=BothPlayer())))


class OgreWarmaul(WeaponCard):
    def __init__(self):
        super().__init__("Ogre Warmaul", 3, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON)

    def create_weapon(self, player):
        return Weapon(4, 2, effects=[Effect(CharacterAttack(IsHero()),
                                            ActionTag(ChangeTarget(CharacterSelector(NotCurrentTarget(), EnemyPlayer(),
                                                                                     RandomPicker())),
                                            HeroSelector(), And(OneIn(2), OpponentMinionCountIsGreaterThan(0))))])
